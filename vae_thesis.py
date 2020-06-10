# -*- coding: utf-8 -*-
"""VAE_thesis.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1VoiB27yxhgci6S-DRIboNLDLr_blOvcP

# Libraries

## Mount GoogleDrive to upload files on it
"""

from google.colab import drive
drive.mount('/content/drive')

# This is useful to remove some of the Warnings that starts when tensorflow is imported
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf

# Libraries for Math
import numpy as np
import matplotlib.pyplot as plt

# Libraries for ML
import keras
from keras.layers import Input, Dense, Conv2D, Conv2DTranspose, LeakyReLU, BatchNormalization, Flatten, Reshape, Lambda, ReLU
from keras.datasets import mnist
from keras.optimizers import Adam
from keras.models import Model
import keras.backend as K

# The path in where the files are saved
PATH = 'drive/My Drive/Thesis/VAE/'

"""# Parameters Setup and Definition of auxiliary functions"""

###########################################################################################################################################
# Setup Parameters
###########################################################################################################################################

input_dim = (32, 32, 1)
intermediate_dim = 128
latent_dim = 16

epochs = 5
batch_size = 100

# Auxiliary options
SAVE = False
SAVE_WEIGHTS = False
EVALUATE = False
TRAIN = False

###########################################################################################################################################
# Additional Functions
###########################################################################################################################################

def sampling(args):
	z_mean, z_log_var = args
	batch = K.shape(z_mean)[0]
	dim = K.int_shape(z_mean)[1]

	epsilon = K.random_normal(shape=(batch, dim), mean=0, stddev=1)

	return z_mean + K.exp(0.5 * z_log_var) * epsilon

def vae_loss(x_true, x_pred):
	x_true = K.reshape(x_true, (-1, np.prod(input_dim)))
	x_pred = K.reshape(x_pred, (-1, np.prod(input_dim)))

	xent_loss = 0.5 * K.sum(K.square(x_true - x_pred), axis=-1)
	rec_loss = -0.5 * K.sum(1 + z_log_var - K.square(z_mean) - K.exp(z_log_var), axis=-1)

	return K.mean(xent_loss + rec_loss)
 
def pad(x, n):
	d = x.shape[1]
	N = len(x)

	data = np.zeros(shape=(N, n, n))
	for i in range(N):
		data[i, :d, :d] = x[i]
	
	return data

"""# Model (Encoder + Decoder = VAE)"""

###########################################################################################################################################
# ENCODER
###########################################################################################################################################

x = Input(shape=input_dim, name='Encoder_Input')

h = Conv2D(128, 4, strides=(2, 2), padding='same', name='Convolutional_Layer')(x)
h = BatchNormalization()(h)
h = ReLU()(h)

h = Conv2D(256, 4, strides=(2, 2), padding='same', name='Second_Convolutional_Layer')(h)
h = BatchNormalization()(h)
h = ReLU()(h)

h = Conv2D(512, 4, strides=(2, 2), padding='same', name='Third_Convolutional_Layer')(h)
h = BatchNormalization()(h)
h = ReLU()(h)

h = Conv2D(1024, 4, strides=(2, 2), padding='same', name='Fourth_Convolutional_Layer')(h)
h = BatchNormalization()(h)
h = ReLU()(h)

shape_before_flattening = K.int_shape(h)[1:]
h = Flatten()(h)

z_mean = Dense(latent_dim, activation=None, name='z_Mean')(h)
z_log_var = Dense(latent_dim, activation=None, name='z_log_variance')(h)

z = Lambda(sampling, output_shape=(latent_dim, ), name='z')([z_mean, z_log_var])

encoder = Model(x, [z_mean, z_log_var, z])


###########################################################################################################################################
# DECODER
###########################################################################################################################################

z_in = Input(shape=(latent_dim, ), name='Decoder_Input')

h = Dense(8*8*1024, activation='relu', name='Fully_Connected_Layer')(z_in)
h = Reshape((8, 8, 1024))(h)

h = Conv2DTranspose(512, 4, strides=(2, 2), padding='same', name='Trans_Convolutional_Layer')(h)
h = BatchNormalization()(h)
h = ReLU()(h)

h = Conv2DTranspose(256, 4, strides=(2, 2), padding='same', name='Second_Trans_Convolutional_Layer')(h)
h = BatchNormalization()(h)
h = ReLU()(h)

x_recon = Conv2DTranspose(1, 4, padding='same', activation='sigmoid', name='x_recon')(h)

decoder = Model(z_in, x_recon)

###########################################################################################################################################
# VAE
###########################################################################################################################################

x_pred = decoder(z)
vae = Model(x, x_pred)

"""# Import dataset and train the model on it."""

###########################################################################################################################################
# DATASET
###########################################################################################################################################

(X_train, Y_train), (X_test, Y_test) = mnist.load_data()

X_train = X_train.astype('float32')/255
X_test = X_test.astype('float32')/255

X_train = pad(X_train, 32)
X_test = pad(X_test, 32)

X_train = np.reshape(X_train, (-1,) + input_dim)
X_test = np.reshape(X_test, (-1,) + input_dim)

###########################################################################################################################################
# Train the model
###########################################################################################################################################

if TRAIN:
    vae.compile(optimizer=Adam(learning_rate=0.001), loss=vae_loss, metrics=['mse'])
    hist = vae.fit(X_train, X_train, batch_size=batch_size, epochs=epochs, verbose=1)
else:
    vae = keras.models.load_model(PATH + "vae_latent" + str(latent_dim) + "v2.h5", custom_objects={'vae_loss': vae_loss}, compile=False)
    encoder = keras.models.load_model(PATH + "encoder_latent" + str(latent_dim) + "v2.h5", custom_objects={'vae_loss': vae_loss}, compile=False)
    decoder = keras.models.load_model(PATH + "decoder_latent" + str(latent_dim) + "v2.h5", custom_objects={'vae_loss': vae_loss}, compile=False)

###########################################################################################################################################
# MODEL ARCHITECTURES
###########################################################################################################################################

if SAVE_WEIGHTS:
    vae.save(PATH + 'vae_latent' + str(latent_dim) + '.h5', overwrite=True)
    encoder.save(PATH + 'encoder_latent' + str(latent_dim) + '.h5', overwrite=True)
    decoder.save(PATH + 'decoder_latent' + str(latent_dim) + '.h5', overwrite=True)

if SAVE:
    from keras.utils import plot_model
    plot_model(vae, PATH + 'vae.png', show_shapes=True)
    plot_model(encoder, PATH + 'encoder.png', show_shapes=True)
    plot_model(decoder, PATH + 'decoder.png', show_shapes=True)

"""# Results

## Loss over epochs
"""

###########################################################################################################################################
# PLOTS
###########################################################################################################################################

if TRAIN:
    loss = hist.history['loss'] # We want to plot the loss history throught epochs
    plt.style.use('ggplot') # Makes plots better

    plt.plot(loss, 'o--')
    plt.title('VAE Loss over epochs')
    plt.xlabel('epochs')
    plt.ylabel('loss')
    if SAVE:
        plt.savefig(PATH + 'loss.png')
    plt.show()

"""## Latent Space Visualization"""

###########################################################################################################################################
# VISUALIZATION
###########################################################################################################################################

if latent_dim == 2:
    z_val = encoder.predict(X_train)[2] # Encoder predict a list [z_mu, z_log_var, z]

    plt.scatter(z_val[:, 0], z_val[:, 1], c=Y_train)
    plt.title('Latent Space Visualization MNIST')
    plt.xlabel('z_1')
    plt.ylabel('z_2')
    plt.colorbar()
    if SAVE:
        plt.savefig(PATH + 'latent_viz.png')
    plt.show()

###########################################################################################################################################
# MEAN
###########################################################################################################################################

if latent_dim == 2:
    z_mean = encoder.predict(X_train)[0]

    plt.scatter(z_mean[:, 0], z_mean[:, 1], c=Y_train)
    plt.title('Latent Space Visualization MNIST, mean plot')
    plt.xlabel('z_1')
    plt.ylabel('z_2')
    plt.colorbar()
    if SAVE:
        plt.savefig(PATH + 'latent_mean.png')
    plt.show()

###########################################################################################################################################
# VARIANCE
###########################################################################################################################################

if latent_dim == 2:
    z_log_var = encoder.predict(X_train)[1]
    z_var = np.exp(0.5 * z_log_var) # Generate variance from log_variance

    plt.scatter(z_var[:, 0], z_var[:, 1], c=Y_train)
    plt.title('Latent Space Visualization MNIST, variance plot')
    plt.xlabel('z_1')
    plt.ylabel('z_2')
    plt.colorbar()
    if SAVE:
        plt.savefig(PATH + 'latent_var.png')
    plt.show()

###########################################################################################################################################
# RECONSTRUCTION
###########################################################################################################################################

n = 10
digit_size = 32

X_test = np.reshape(X_test, (-1, 32, 32, 1))
X_recon = vae.predict(X_test)
X_recon = np.reshape(X_recon, (-1, 32, 32))
X_test = np.reshape(X_test, (-1, 32, 32))
figure = np.zeros((2 * digit_size, n * digit_size))

for i in range(n):
    sample = np.random.randint(0, len(X_recon))
    figure[:digit_size, i * digit_size: (i+1) * digit_size] = X_test[sample]
    figure[digit_size:, i * digit_size: (i+1) * digit_size] = X_recon[sample]

plt.style.use('default')
plt.imshow(figure, cmap='gray')
if SAVE:
    plt.savefig(PATH + 'mnist_reconstruction.png')
plt.show()

###########################################################################################################################################
# GENERATION
###########################################################################################################################################

if latent_dim == 2:
    # display a 2D manifold of the digits
    n = 30  # figure with n x n digits
    digit_size = 32
    figure = np.zeros((digit_size * n, digit_size * n))
    # we will sample n points within [-n, n] standard deviations
    grid_x = np.linspace(-3, 3, n)
    grid_y = np.linspace(-3, 3, n)

    for i, yi in enumerate(grid_x):
        for j, xi in enumerate(grid_y):
            z_sample = np.array([[xi, yi]])
            x_decoded = decoder.predict(z_sample)
            digit = x_decoded[0].reshape(digit_size, digit_size)
            figure[i * digit_size: (i + 1) * digit_size,
                j * digit_size: (j + 1) * digit_size] = digit

    plt.figure(figsize=(10, 10))
    plt.imshow(figure, cmap='gray')
    if SAVE:
        plt.savefig(PATH + 'generated_minst.png')
    plt.show()

else:
    n = 10 #figure with n x n digits
    digit_size = 32
    figure = np.zeros((digit_size * n, digit_size * n))
    # we will sample n points randomly sampled

    z_sample = np.random.normal(size=(n**2, latent_dim), scale=1)
    for i in range(n):
        for j in range(n):
            x_decoded = decoder.predict(np.array([z_sample[i + n * j]]))
            digit = x_decoded[0].reshape(digit_size, digit_size)
            figure[i * digit_size: (i + 1) * digit_size,
                j * digit_size: (j + 1) * digit_size] = digit

    plt.figure(figsize=(10, 10))
    plt.imshow(figure, cmap='gray')
    if SAVE:
        plt.savefig(PATH + 'generated_minst.png')
    plt.show()

###########################################################################################################################################
# EVALUATE FID SCORE
###########################################################################################################################################

# Import evaluate.py, which contains functions to reshape and evaluate image generated
import sys
sys.path.insert(1, PATH)
import evaluate

from keras.applications.inception_v3 import preprocess_input
from keras.applications.inception_v3 import InceptionV3

if EVALUATE:
    sample_size = 4000

    z_sample = np.random.normal(0, 1, size=(sample_size, latent_dim))
    sample = np.random.randint(0, len(X_test), size=sample_size)
    X_gen = decoder.predict(z_sample)
    X_real = X_test[sample]

    X_gen = evaluate.scale_images(X_gen, (299, 299, 1))
    X_real = evaluate.scale_images(X_real, (299, 299, 1))
    print('Scaled', X_gen.shape, X_real.shape)

    X_gen_t = preprocess_input(X_gen)
    X_real_t = preprocess_input(X_real)

    X_gen = np.zeros(shape=(sample_size, 299, 299, 3))
    X_real = np.zeros(shape=(sample_size, 299, 299, 3))
    for i in range(3):
        X_gen[:, :, :, i] = X_gen_t[:, :, :, 0]
        X_real[:, :, :, i] = X_real_t[:, :, :, 0]
    print('Final', X_gen.shape, X_real.shape)

########################################################################################################################
# MODEL (IMPORT INCEPTIONv3)
########################################################################################################################

    # prepare the inception v3 model
    model = InceptionV3(include_top=False, pooling='avg', input_shape=(299,299,3))

########################################################################################################################
# PRINT FID SCORE
########################################################################################################################

    # fid between images1 and images2
    fid = evaluate.calculate_fid(model, X_real, X_gen)
    print('FID (different): %.3f' % fid)

########################################################################################################################
# CHECK THE NUMBER OF DEACTIVATED LATENT DIMENSION
########################################################################################################################

# Remeber that we already defined z_log_var before.
# z_var = np.exp(z_log_var)

########################################################################################################################
# Define funcions needed for this evaluation
########################################################################################################################

def count_deactivated_variables(z_var, treshold = 0.8):
    z_var = np.mean(z_var, axis=0)

    return np.sum(z_var > treshold)

def loss_variance(x_true, x_recon):
    x_true = np.reshape(x_true, (-1, np.prod(x_true.shape[1:])))
    x_recon = np.reshape(x_recon, (-1, np.prod(x_recon.shape[1:])))

    var_true = np.mean(np.var(x_true, axis=1), axis=0)
    var_recon = np.mean(np.var(x_recon, axis=1), axis=0)

    return np.abs(var_true - var_recon)

########################################################################################################################
# SHOW THE RESULTS
########################################################################################################################

X_test = np.reshape(X_test, (-1,) +  input_dim)
z_mean, z_log_var, _ = encoder.predict(X_test)
z_var = np.exp(z_log_var)
n_deact = count_deactivated_variables(z_var)
print('We have a total of ', latent_dim, ' latent variables. ', count_deactivated_variables(z_var), ' of them are deactivated')

var_law = np.mean(np.var(z_mean, axis=0) + np.mean(z_var, axis=0))
print('Variance law has a value of: ', var_law)

X_recon = vae.predict(X_train)
print('We lost ', loss_variance(X_test, X_recon), 'Variance of the original data')