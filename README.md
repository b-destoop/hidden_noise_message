# denoising

## principle

The app reveals a hidden message when the right sound is played in front of it, but only for the duration of the sound.

This is done by showing static noise (like on old tv's) when no sound is registered. When a sound is picked up by the
system's microphone, the noise shifts into the hidden message, but only by the amount of similarity of the sound that is
picked up and the secret sound that is to be played.

> _optional improvement_ : have the code show when no noise is made!

## noise visibility tactic

Create noise using a gaussian curve. For the values which coincide with the code image, this gaussian curve should have
a smaller standard deviation.

## todo

- [x] create a window with static noise
- [ ] receive sound
- [ ] find comparison metric between sound and preferred sound (fourier? convolution? machine learning?)
- [ ] load in image with a message
- [x] distort image according to the comparison metric
- [ ] create an extra window with tuning specifics
    - [ ] load in image
    - [ ] choose a microphone source
    - [ ] sensitivity dialling
    - [ ] goal sample loading
- [ ] create transfer function for the similarity to the amount of revealing of the hidden message. 