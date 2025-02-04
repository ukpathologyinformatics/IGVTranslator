import os

from liftover import ChainFile


class Lifter:
    chain_file = None

    @staticmethod
    def is_chain_file_set():
        return Lifter.chain_file is not None

    @staticmethod
    def load_chain(chain_file: str):
        if not os.path.isfile(chain_file):
            raise FileNotFoundError(f"Chain file {chain_file} not found")
        Lifter.chain_file = ChainFile(chain_file, one_based=True)

    @staticmethod
    def liftover_coordinate(chrom: str, pos: int):
        if Lifter.chain_file is None:
            raise Exception("Chain file not initialized")
        out = Lifter.chain_file[chrom][pos]
        out_chrom = str(out[0][0]).replace('chr','')
        out_pos = str(out[0][1])
        return out_chrom, out_pos
