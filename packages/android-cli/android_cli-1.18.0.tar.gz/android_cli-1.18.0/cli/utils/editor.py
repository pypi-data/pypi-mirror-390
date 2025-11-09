import subprocess
import tempfile

from cli.entities.setting import Settings


def get_multiline_input(default=''):
    with tempfile.NamedTemporaryFile(mode='r+', delete=False) as tf:  # 'delete=False' para evitar que el archivo se elimine cuando se cierra
        # Escribimos el texto predeterminado en el archivo temporal
        tf.write(default)
        tf.flush()  # Asegurarnos de que se haya escrito en el disco

        # Abre el archivo en el editor
        subprocess.call([Settings().config['editor'], '-w', tf.name])
        tf.seek(0)
        content = tf.read()

    return content
