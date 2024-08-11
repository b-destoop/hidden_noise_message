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

> _note_ : the code that is to be shown should be white on a black background.

## sound

Sound is captured using the default microphone of the system.

The `volume` is calculated using `volume = 20 * log10(avg(sample))`. This parameter is very volatile, therefore the
following helper parameters are also calculated:

- `max volume`: the highest value of `volume` that was measured with the currently running application
- `min volume`: the lowest value of `volume` that was measured with the currently running application
- `relative volume`: a number indicating where the current `volume` sits between `max volume` and `min volume`. 1 means
  the current value of `volume` is the same as `max volume`. The same applies for 0 being represent of `min volume`
- `average relative volume`: a time averaged version of relative volume. This gives a slower changing parameter. This
  parameter is to be used for the visibility application.

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