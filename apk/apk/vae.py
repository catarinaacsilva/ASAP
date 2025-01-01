import keras
import tensorflow as tf

@keras.saving.register_keras_serializable()
class Sampling(keras.layers.Layer):
    """Uses (z_mean, z_log_var) to sample z, the vector encoding a digit."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.seed_generator = keras.random.SeedGenerator(1337)

    def call(self, inputs):
        z_mean, z_log_var = inputs
        batch = keras.ops.shape(z_mean)[0]
        dim = keras.ops.shape(z_mean)[1]
        epsilon = keras.random.normal(shape=(batch, dim), seed=self.seed_generator)
        return z_mean + keras.ops.exp(0.5 * z_log_var) * epsilon


@keras.saving.register_keras_serializable()
class VAE(keras.Model):
    def __init__(self, encoder, decoder, **kwargs):
        super().__init__(**kwargs)
        self.encoder = encoder
        self.decoder = decoder
        self.total_loss_tracker = keras.metrics.Mean(name='total_loss')
        self.reconstruction_loss_tracker = keras.metrics.Mean(name='reconstruction_loss')
        self.kl_loss_tracker = keras.metrics.Mean(name='kl_loss')
        self.r2_score_tracker = keras.metrics.Mean(name='r2_score')

    @property
    def metrics(self):
        return [
            self.total_loss_tracker,
            self.reconstruction_loss_tracker,
            self.kl_loss_tracker,
            self.r2_score_tracker
        ]

    def train_step(self, data):
        if isinstance(data, tuple):
            data = data[0]

        with tf.GradientTape() as tape:
            z_mean, z_log_var, z = self.encoder(data)
            reconstruction = self.decoder(z)
            reconstruction_loss = keras.ops.mean(keras.ops.sum(keras.ops.square(data - reconstruction), axis=1))
            
            kl_loss = -0.5 * (1 + z_log_var - keras.ops.square(z_mean) - keras.ops.exp(z_log_var))
            kl_loss = keras.ops.mean(keras.ops.sum(kl_loss, axis=1))
            
            total_loss = reconstruction_loss + kl_loss

            sum_squares_residuals = keras.ops.sum((data - reconstruction) ** 2)
            sum_squares = keras.ops.sum((data - keras.ops.mean(data)) ** 2)
            r2_score_loss = 1.0 - sum_squares_residuals / sum_squares
        grads = tape.gradient(total_loss, self.trainable_weights)
        self.optimizer.apply_gradients(zip(grads, self.trainable_weights))
        self.total_loss_tracker.update_state(total_loss)
        self.reconstruction_loss_tracker.update_state(reconstruction_loss)
        self.kl_loss_tracker.update_state(kl_loss)
        self.r2_score_tracker.update_state(r2_score_loss)
        return {
            "loss": self.total_loss_tracker.result(),
            "reconstruction_loss": self.reconstruction_loss_tracker.result(),
            "kl_loss": self.kl_loss_tracker.result(),
            "r2_score": self.r2_score_tracker.result()
        }
    
    def test_step(self, data):
        
        if isinstance(data, tuple):
            data = data[0]

        z_mean, z_log_var, z = self.encoder(data)
        reconstruction = self.decoder(z)
        reconstruction_loss = keras.ops.mean(keras.ops.sum(keras.ops.square(data - reconstruction), axis=1))
        kl_loss = -0.5 * (1 + z_log_var - keras.ops.square(z_mean) - keras.ops.exp(z_log_var))
        kl_loss = keras.ops.mean(keras.ops.sum(kl_loss, axis=1))
        total_loss = reconstruction_loss + kl_loss

        sum_squares_residuals = keras.ops.sum((data - reconstruction) ** 2)
        sum_squares = keras.ops.sum((data - keras.ops.mean(data)) ** 2)
        r2_score_loss = 1.0 - sum_squares_residuals / sum_squares
        
        return {
            "loss": total_loss,
            "reconstruction_loss": reconstruction_loss,
            "kl_loss": kl_loss,
            "r2_score": r2_score_loss
        }

    def call(self, data):
        z_mean, z_log_var, z = self.encoder(data)
        reconstruction = self.decoder(z)
        return reconstruction

    def get_config(self):
        # Get the base model configuration
        config = super().get_config()

        # Manually serialize the encoder and decoder models
        encoder_config = self.encoder.get_config()
        decoder_config = self.decoder.get_config()

        # Add the encoder and decoder configurations to the model config
        config.update({
            'encoder': encoder_config,
            'decoder': decoder_config,
        })
        return config

    @classmethod
    def from_config(cls, config):
        # Rebuild the encoder and decoder from their config
        # print("Config: ", config)
        encoder_config = config.pop('encoder')
        decoder_config = config.pop('decoder')

        # Recreate the encoder and decoder models using their configurations
        encoder = keras.Model.from_config(encoder_config)
        decoder = keras.Model.from_config(decoder_config)

        # Now return an instance of VAE using the restored encoder and decoder
        return cls(encoder=encoder, decoder=decoder, **config)

