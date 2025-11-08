from warnings import warn
from typing import List, Callable, Any, Generator, Union, Tuple
from typing_extensions import TypeAlias
from joblib import Parallel, delayed
from tqdm import tqdm

ARGSET_TYPE: TypeAlias = Union[List[Any], Generator[Any, None, None], Tuple[Any, ...]]

def parallel_luncher(
    job: Callable, argset: ARGSET_TYPE, pnum: int, unpack=False, use_tq=True, **kwargs
) -> list:
    """Parallel's delayed method luncher."""

    def job_wrraper(job: Callable, unpack: bool = False) -> Callable:
        """Wrapper for job that have dict type args."""
        if unpack:
            if isinstance(argset[0], dict):
                return lambda _args: job(**_args)
            elif isinstance(argset[0], (list, tuple)):
                return lambda _args: job(*_args)
            else:
                warn("Parallel job argments cannot be unpacked.")
        return job

    result = []
    iterator = tqdm(argset, **kwargs) if use_tq else argset

    result = Parallel(n_jobs=pnum, verbose=0)(
        delayed(job_wrraper(job, unpack))(arg) for arg in iterator
    )
    return list(result)
