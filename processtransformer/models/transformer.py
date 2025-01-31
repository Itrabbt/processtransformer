
import tensorflow as tf
from tensorflow.keras import layers

class TransformerBlock(layers.Layer):
    def __init__(self, embed_dim, num_heads, ff_dim, rate=0.1):
        # 定义了transformer模型中的几个层和操作。
        # embed_dim：Transformer 模型中嵌入维度的大小。
        # num_heads：多头自注意力机制中注意力头的数量。
        # ff_dim：前馈神经网络（Feed-Forward Network）中隐藏层的维度。
        # rate：Dropout 层的丢弃率，默认值为 0.1。
        super(TransformerBlock, self).__init__()
        # 多头注意力
        self.att = layers.MultiHeadAttention(num_heads=num_heads, key_dim=embed_dim)
        # Feed forward层
        self.ffn = tf.keras.Sequential(
            [layers.Dense(ff_dim, activation="relu"), layers.Dense(embed_dim),]
        )
        # 两个 Layer Normalization 层
        self.layernorm_a = layers.LayerNormalization(epsilon=1e-6)
        self.layernorm_b = layers.LayerNormalization(epsilon=1e-6)
        # 两个 Dropout 层
        self.dropout_a = layers.Dropout(rate)
        self.dropout_b = layers.Dropout(rate)

    def call(self, inputs, training):
        # call 方法是 TensorFlow 中定义层的前向传播逻辑的方法，inputs：输入张量，表示传递给 Transformer 模块的数据。training：一个布尔值，指示当前是否处于训练模式。
        attn_output = self.att(inputs, inputs)
        attn_output = self.dropout_a(attn_output, training=training)
        out_a = self.layernorm_a(inputs + attn_output)
        ffn_output = self.ffn(out_a)
        ffn_output = self.dropout_b(ffn_output, training=training)
        return self.layernorm_b(out_a + ffn_output)

class TokenAndPositionEmbedding(layers.Layer):
    # 用于处理输入数据并生成嵌入表示。
    def __init__(self, maxlen, vocab_size, embed_dim):
        super(TokenAndPositionEmbedding, self).__init__()
        self.token_emb = layers.Embedding(input_dim=vocab_size, output_dim=embed_dim)
        self.pos_emb = layers.Embedding(input_dim=maxlen, output_dim=embed_dim)

    def call(self, x):
        maxlen = tf.shape(x)[-1]
        positions = tf.range(start=0, limit=maxlen, delta=1)
        positions = self.pos_emb(positions)
        x = self.token_emb(x)
        return x + positions

def get_next_activity_model(max_case_length, vocab_size, output_dim, 
    embed_dim = 36, num_heads = 4, ff_dim = 64):
    inputs = layers.Input(shape=(max_case_length,))
    x = TokenAndPositionEmbedding(max_case_length, vocab_size, embed_dim)(inputs)
    x = TransformerBlock(embed_dim, num_heads, ff_dim)(x)
    x = layers.GlobalAveragePooling1D()(x)
    x = layers.Dropout(0.1)(x)
    x = layers.Dense(64, activation="relu")(x)
    x = layers.Dropout(0.1)(x)
    outputs = layers.Dense(output_dim, activation="linear")(x)
    transformer = tf.keras.Model(inputs=inputs, outputs=outputs,
        name = "next_activity_transformer")
    return transformer

def get_next_time_model(max_case_length, vocab_size, output_dim = 1, 
    embed_dim = 36, num_heads = 4, ff_dim = 64):

    inputs = layers.Input(shape=(max_case_length,))
    # Three time-based features
    time_inputs = layers.Input(shape=(3,)) 
    x = TokenAndPositionEmbedding(max_case_length, vocab_size, embed_dim)(inputs)
    x = TransformerBlock(embed_dim, num_heads, ff_dim)(x)
    x = layers.GlobalAveragePooling1D()(x)
    x_t = layers.Dense(32, activation="relu")(time_inputs)
    x = layers.Concatenate()([x, x_t])
    x = layers.Dropout(0.1)(x)
    x = layers.Dense(128, activation="relu")(x)
    x = layers.Dropout(0.1)(x)
    outputs = layers.Dense(output_dim, activation="linear")(x)
    transformer = tf.keras.Model(inputs=[inputs, time_inputs], outputs=outputs,
        name = "next_time_transformer")
    return transformer

def get_remaining_time_model(max_case_length, vocab_size, output_dim = 1, 
    embed_dim = 36, num_heads = 4, ff_dim = 64):

    inputs = layers.Input(shape=(max_case_length,))
    # Three time-based features
    time_inputs = layers.Input(shape=(3,)) 
    x = TokenAndPositionEmbedding(max_case_length, vocab_size, embed_dim)(inputs)
    x = TransformerBlock(embed_dim, num_heads, ff_dim)(x)
    x = layers.GlobalAveragePooling1D()(x)
    x_t = layers.Dense(32, activation="relu")(time_inputs)
    x = layers.Concatenate()([x, x_t])
    x = layers.Dropout(0.1)(x)
    x = layers.Dense(128, activation="relu")(x)
    x = layers.Dropout(0.1)(x)
    outputs = layers.Dense(output_dim, activation="linear")(x)
    transformer = tf.keras.Model(inputs=[inputs, time_inputs], outputs=outputs,
        name = "remaining_time_transformer")
    return transformer