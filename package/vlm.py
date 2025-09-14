import os
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from torchvision import transforms
from torchvision.models.video import r3d_18, R3D_18_Weights, r2plus1d_18, R2Plus1D_18_Weights
from torch.utils.data import Dataset, DataLoader
from torch.amp import autocast, GradScaler
import cv2
from package.utilities import Utility
import time

config = Utility.load_yaml()["vlm"]

# Set CUDA_LAUNCH_BLOCKING to '1' for debugging
os.environ['CUDA_LAUNCH_BLOCKING'] = str(config["model"]["device_debug"])

# Paths
TRAINING_PATH = os.path.join(os.getcwd(), config['training_path'])
LOCAL_MEMORY_PATH = os.path.join(TRAINING_PATH, 'model_weights.pth')


class VLMGaming:
    video_to_validate = None
    dataloader = None
    genreDataset = None
    model = None

    class RetryException(Exception):
        pass

    def __init__(self, use_model_finetuned=False):
        VLMGaming.genreDataset = self.VideoDataset()
        if use_model_finetuned:
            VLMGaming.model = r2plus1d_18(weights=R2Plus1D_18_Weights.DEFAULT)
        else:
            VLMGaming.model = r2plus1d_18()
    
        VLMGaming.model.fc = nn.Linear(VLMGaming.model.fc.in_features,  len(VLMGaming.genreDataset.labels))
        self.predicted_genres = []

     # Main method to write the video data and add it to the model (Dataset > Dataloader > Model R2PLUS1D) - based on a folder > multiple videos
    @staticmethod
    def teach_model_multiple_videos(video_filenames_with_label):
        for video_filename_with_label in video_filenames_with_label:
            video_filename_path = video_filename_with_label[0]
            label = video_filename_with_label[1]
            idx = video_filename_with_label[2]
            if video_filename_path is None: # Only folder detected which is used for labels
                continue
            if not video_filename_path.endswith(('.mp4', '.avi')):
                print(f"The video file {video_filename_path} does not have the expected file type MP4 or AVI. Skipping model training...")
                continue

            video_path_converted = Utility.change_video_codec(video_filename_path)
            clip = VLMGaming.genreDataset.prepare_samples(video_path_converted, idx)
            VLMGaming._prepare_clip(clip)

        VLMGaming._finetune_model()



    # Main method to write the video data and add it to the model (Dataset > Dataloader > Model R2PLUS1D) - based on a single file > one video
    @staticmethod
    def teach_model_single_video(video_filename_path, label_name):
        if not video_filename_path.endswith(('.mp4', '.avi')):
            print(f"The video file {video_filename_path} does not have the expected file type MP4 or AVI. Skipping model training...")
            return
        label_idx = VLMGaming.genreDataset.get_label_idx(label_name)
        video_path_converted = Utility.change_video_codec(video_filename_path) # Check if it had the codecs supported by the model
        clip = VLMGaming.genreDataset.prepare_samples(video_path_converted, label_idx) # Add the samples from the video to the dataset and prepare them to respect the model boundaries - still no training is done here
        VLMGaming._prepare_clip(clip) # Process the video based on the samples created and prepare it to respect the model bounderies - still no training is done here
        VLMGaming._finetune_model() # Read the ready video by loading the processed samples to the dataloader and make the GPU read them and write to the dataset - training is done here

    @staticmethod
    def _create_dataLoader():
        batch_size = config["model"]['batch_size']
        num_workers = config["model"]['num_workers']
        return DataLoader(
            VLMGaming.genreDataset, 
            batch_size=batch_size, 
            shuffle=True, 
            num_workers=num_workers, 
            persistent_workers=True,  # Keeps workers alive between epochs
            pin_memory=True) # data load from dataset starts
    
    @staticmethod
    def _finetune_model():
        if len(VLMGaming.genreDataset.samples) <= 0:
            raise VLMGaming.RetryException("There are no samples in the dataset for the model to be trained of!\nDisable 'ignore_download_videos' or add videos manually to the training folder! Skipping...")
        
        VLMGaming.dataloader = VLMGaming._create_dataLoader()
        epochs = config["model"]['epochs']
        device_type = config["model"]['device_type']
        is_debug = config["model"]["device_debug"] == 1

        print("Start training the model...")
        if torch.cuda.is_available():
            if is_debug:
                print("[DEBUG] GPU is available!")
            device = torch.device(device_type)
        else:
            if is_debug:
                print("[DEBUG] GPU not available, using CPU.")
            device = torch.device("cpu")

        VLMGaming.model.to(device)

        learning_rate = config["model"]['learning_rate']
        momentum = config["model"]['momentum']
        optimizer = optim.SGD(VLMGaming.model.parameters(), lr=learning_rate, momentum=momentum)
        criterion = nn.CrossEntropyLoss()
        scaler = GradScaler(device_type)

        VLMGaming.model.train()
        for epoch in range(epochs):
            for i, (inputs, labels) in enumerate(VLMGaming.dataloader):
                start_time = time.time()
                labels = labels.to(device)
                inputs = inputs.to(device)
                if is_debug:
                    print(f"[DEBUG] Input shape: {inputs.shape}; Items {inputs[:5]}...") # Check input/label dimensions
                    print(f"[DEBUG] Label shape: {labels.shape}; Items {labels[:5]}...") # Check input/label dimensions
                    print(f"[DEBUG] Epoch: {epoch}, Batch: {i}")

                optimizer.zero_grad()
                with autocast(device_type):
                    outputs = VLMGaming.model(inputs)
                    loss = criterion(outputs, labels)
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()

                end_time = time.time()
                batch_time = end_time - start_time
                if is_debug:
                    print(f"[DEBUG] Time: {batch_time:.4f} seconds")
                    print(f"[DEBUG] Loss: {loss.item()}")
                    print(f"[DEBUG] Output: Shape {outputs.shape}; Items {outputs[:5]}...")

            torch.cuda.empty_cache()
            print(f"{int((int(epoch+1)/epochs)*100)}% completed...")
        torch.save(VLMGaming.model.state_dict(), LOCAL_MEMORY_PATH)

        print("Fine-tuning completed!")

    @staticmethod
    def _prepare_clip(clip):
        # Define the spatial transform
        clip_resolution = config["model"]["frames_resolution"].split("x")
        spatial_transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((int(clip_resolution[1]), int(clip_resolution[0]))),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.45, 0.45, 0.45], std=[0.225, 0.225, 0.225]),
        ])
        # apply transform to each frame
        frames = torch.unbind(clip, dim=1)
        frames = [spatial_transform(frame[:3, :, :]) for frame in frames] # using 3 channel RGB frame
        clip = torch.stack(frames, dim=1)

        # clip_resolution = config["clip_resolution"].split("x")
        # spatial_transform = transforms.Compose([
        #     transforms.Resize((int(clip_resolution[1]), int(clip_resolution[0]))),
        #     transforms.Normalize(mean=[0.485, 0.456, 0.406],
        #                             std=[0.229, 0.224, 0.225])
        # ])

        # # permute to [C, T, H, W]
        # clip = clip.permute(3, 0, 1, 2).float()

        # # apply transform to each frame
        # frames = torch.unbind(clip, dim=1)
        # frames = [spatial_transform(frame) for frame in frames]
        # clip = torch.stack(frames, dim=1)
        return clip

    @staticmethod
    def _extract_clip(video_converted_path, num_frames):
        """
        Static method to read a fixed number of frames from a video file using OpenCV.
        """

        if not Utility.does_file_exist(video_converted_path):
            raise Exception(f"File {video_converted_path} does not exist!")
        cap = cv2.VideoCapture(video_converted_path)
        if not cap.isOpened():
            raise Exception(f"Cannot open video file: {video_converted_path}")
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames == 0:
            raise Exception(f"Failed to read the video '{video_converted_path}'")
        frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)

        frames = []
        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if ret:
                # print("Frame shape:", frame.shape)
                # print("Pixel at (0,0):", frame[0,0])
                # cv2.imshow('Frame', frame)
                # cv2.waitKey(0)
                # cv2.destroyAllWindows()
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Correct order
                frame = torch.from_numpy(frame).float()
                frames.append(frame)
            else:
                break
        cap.release()

        return torch.stack(frames)
    
    # Output format will be a list of tuples: [video_path, label] in the folder path
    @staticmethod
    def _gather_videos_to_train(folder_path):
        label_idx = 0
        videos_to_train = []
        for class_dir in sorted(os.listdir(folder_path)):
            class_path = os.path.join(folder_path, class_dir)
            if os.path.isdir(class_path):
                videos_to_train.append((None, class_dir, label_idx)) # Just to add the genre to the list
                for filename in sorted(os.listdir(class_path)):
                    videos_to_train.append((os.path.join(class_path, filename), class_dir, label_idx))
                label_idx += 1
        return videos_to_train

    class VideoDataset(Dataset):

        def __init__(self, root_dir=TRAINING_PATH, clip_len=16):
            self.root_dir = root_dir
            self.clip_len = clip_len
            videos_to_train = VLMGaming._gather_videos_to_train(self.root_dir)
            self.labels = []
            for video_path, label_name, label_idx in videos_to_train:
                if video_path is None:
                    self.labels.append((label_name, label_idx))
            self.samples = []

            # Gather samples and labels

        def __len__(self):
            return len(self.samples)

        def __getitem__(self, idx):
            video_path, label_idx = self.samples[idx]
            clip = self.read(video_path, config["model"]['frames_per_second'])
            return clip, label_idx
        
        def get_label(self, idx):
            return self.labels[idx]
        
        def get_label_idx(self, label_name):
            for label in self.labels:
                if label[0] == label_name:
                    return label[1]
            return None
        
        def get_label_name(self, label_idx):
            for label in self.labels:
                if label[1] == label_idx:
                    return label[0]
            return None
        
        def read(self, video_path_converted, num_frames):
            clip = VLMGaming._extract_clip(video_path_converted, num_frames)
            return VLMGaming._prepare_clip(clip)


        def prepare_samples(self, video_path_converted, class_idx):
            """
            Loads a video and preprocesses it into a clip suitable for the model.
            """
            self.samples.append((video_path_converted, class_idx))
            video_tensor = VLMGaming._extract_clip(video_path_converted, config["model"]['frames_per_second'])
            total_frames = len(video_tensor)

            # Select clip of length clip_len
            if total_frames >= self.clip_len:
                start = torch.randint(0, total_frames - self.clip_len + 1, (1,)).item()
                clip = video_tensor[start:start + self.clip_len]
            else:
                # Pad if too short
                pad_len = self.clip_len - total_frames
                pad_shape = (pad_len, *video_tensor.shape[1:])
                pad = torch.zeros(pad_shape, dtype=video_tensor.dtype)
                clip = torch.cat([video_tensor, pad], dim=0)

            return clip                  

    def start_model(self, force_retrain=False, force_download_videos=None, use_model_finetuned=False, games_per_genre={}):
        # Load existing model weights if available
        if use_model_finetuned:
            model_path = LOCAL_MEMORY_PATH

            if os.path.exists(model_path) and not force_retrain:
                VLMGaming.model.load_state_dict(torch.load(model_path))
                print("Loaded existing model weights.")
                return

            # Download videos based on labels
            if force_download_videos and games_per_genre:
                print("Start downloading the videos...")
                for label_name, label_idx in VLMGaming.genreDataset.labels:
                    # Remove old data
                    list_of_files_paths = Utility.get_list_files(label_name, root_dir=TRAINING_PATH, is_dir=True)
                    for file_path, file_idx in list_of_files_paths:
                        os.remove(file_path)

                    searchText = f"{' OR '.join(games_per_genre[label_name])} gameplay"
                    output_path = os.path.join(TRAINING_PATH, label_name + '/')
                    Utility.download_video(searchText, config["clip_resolution"], config["clip_duration_minutes"], len(games_per_genre[label_name]), config["clip_uploaded_days_ago"], output_path)
                print("Downloads completed!")

            # Remove old weights if any
            if os.path.exists(model_path):
                os.remove(model_path)

            # Gather videos to train within the folder
            videos_to_train = VLMGaming._gather_videos_to_train(TRAINING_PATH)
            VLMGaming.teach_model_multiple_videos(videos_to_train)

    # @staticmethod
    # def _get_num_classes():
    #     return len([item for item in os.listdir(TRAINING_PATH) if os.path.isdir(os.path.join(TRAINING_PATH, item))])
    @staticmethod
    def _get_label(idx):
        for label_name, label_idx in VLMGaming.genreDataset.labels:
            if label_idx == idx:
                return label_name
        return None

    @staticmethod
    def _get_probability_percentage(value):
        return int(round(value, 2) * 100)
    
    def get_predicted_genres(self):
        return self.predicted_genres
    
    # Matching the probability value with the label depends on the index value of each list
    def set_predicted_genres(self, predicted_probabilities):
        for idx, predicted_probability in enumerate(predicted_probabilities):
            self.predicted_genres.append((VLMGaming.genreDataset.labels[idx][0], VLMGaming._get_probability_percentage(float(predicted_probability.item())))) # Note: 0 represent the label_name and 1 the label_idx

    def predict_game_genre(self, video_filename_path):
        self.predicted_genres = []
        VLMGaming.video_to_validate = VLMGaming.genreDataset.read(video_filename_path, config['model']['frames_per_second'])
        if VLMGaming.video_to_validate is None:
            return None
        VLMGaming.video_to_validate = VLMGaming.video_to_validate.unsqueeze(0).to(next(VLMGaming.model.parameters()).device)
        with torch.no_grad():
            output = VLMGaming.model(VLMGaming.video_to_validate)
        predicted_probabilities = torch.nn.functional.softmax(output[0], dim=0)
        self.set_predicted_genres(predicted_probabilities)

        probabilities_labels = Utility.get_list_by_column(self.predicted_genres, 0)
        probabilities_values = Utility.get_list_by_column(self.predicted_genres, 1)
        predicted_value = max(probabilities_values)
        predicted_idx = probabilities_values.index(predicted_value)
        predicted_label = probabilities_labels[predicted_idx]

        return predicted_label, predicted_value

    # @staticmethod
    # def extract_features(clip):
    #     # Remove the final classification layer to get features
    #     modules = list(VLMGaming.model.children())[:-1]
    #     feature_extractor = torch.nn.Sequential(*modules)

    #     with torch.no_grad():
    #         features = feature_extractor(clip)
    #     return features.squeeze()
