
Feature implemented:
1) Train bot with videos coming from youtube for get genre
2) teach bot from user input
3) Save dataset locally
4) 

Next features:
0. bot only asks if confidence is lower than 50 and gives all possible answers
1. bot ask if the result was good. if so, reward him.
2. if not, he asks the user what was the expected result. punishes bot
3. ask bot to score game based on focus
4. extract features

LIMITATIONS:

1) Youtube downloader script is not 100% accurate. We still get some trashy videos. Query could be improved.
2) training with multiple videos is very slow: increase batching or num of workers, reduce resolution, use another model....

ERRORS:
1) calling python scripts is failing in result code - DONE
2) make sure we can convert av to H267 codecs before reading any video since it is not supported by the gpu - DONE
2) use llm to get a list of videos games of specific genre because we are getting bad results if query is not specific - DONE
3) lower number of videos to download - DONE
4) test with decrease number of batches and video resolution - DONE
5) check if you can create the new model from scratch - DONE
5) check the youtube downloader since it entered a loop! - DONE
6) error when reading a specific video? - DONE
[h264 @ 0x64cd7e177980] mmco: unref short failure

6) training with multiple videos is very slow: increase batching or num of workers, reduce resolution, use another model....


6) error when training
Traceback (most recent call last):
  File "/home/rgomes/ubisoft_repos/innovation/FeedbackerAi/main.py", line 118, in main
    vlm_gaming.teach_model(genre)
  File "/home/rgomes/ubisoft_repos/innovation/FeedbackerAi/package/vlm.py", line 277, in teach_model
    self._finetune(epochs=epochs)
  File "/home/rgomes/ubisoft_repos/innovation/FeedbackerAi/package/vlm.py", line 225, in _finetune
    labels = labels.to(device)
AttributeError: 'tuple' object has no attribute 'to'
All good! If you need more help, you know where to find me!
Note: Keep in mind I am a simple PoC. If you find any errors or want to improve me, contact the developer Rui Gomes.
(venv) rgomes@BBD-MWS-11801:~/ubisoft_repos/innovation/FeedbackerAi$ 