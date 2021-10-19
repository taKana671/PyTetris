# cython: boundscheck=False
# cython: wraparound=False
# cython: language_level=3


cpdef void update_blockset_row(int[:, :, ::1] blockset, int step):
    
    cdef int i, j
    
    for i in range(4):
        for j in range(4):
            blockset[i, j, 0] += step


cpdef void update_blockset_col(int[:, :, ::1] blockset, int step):

    cdef int i, j
    
    for i in range(4):
        for j in range(4):
            blockset[i, j, 1] += step