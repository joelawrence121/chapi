import gpt_2_simple as gpt2
import tensorflow as tf

from domain.client_json import AggregationRequest


class GPT2Service:
    SAMPLES = 1
    TEMPERATURE = 0.8
    INPUT = "ORIGINAL: {}\n"
    EOS_TAG = '<|endoftext|>'

    def __init__(self, directory):
        tf.compat.v1.reset_default_graph()
        self.sess = gpt2.start_tf_sess()
        gpt2.load_gpt2(self.sess, run_name='run1', checkpoint_dir=directory)

    def aggregate_sentence(self, request: AggregationRequest):
        return {'index': request.index,
                'aggregation': self.generate_paraphrases(original_text=request.original, n_samples=self.SAMPLES)[0]}

    def generate_paraphrases(self, original_text: str, n_samples: int):
        samples = gpt2.generate(
            self.sess,
            length=len(original_text),
            temperature=self.TEMPERATURE,
            prefix=self.INPUT.format(original_text),
            truncate=self.EOS_TAG,
            nsamples=n_samples,
            batch_size=n_samples,
            return_as_list=True
        )
        return [sample.split('\n')[1].replace('PARAPHRASED: ', '') for sample in samples]


if __name__ == '__main__':
    gpt2 = GPT2Service('../checkpoint')
