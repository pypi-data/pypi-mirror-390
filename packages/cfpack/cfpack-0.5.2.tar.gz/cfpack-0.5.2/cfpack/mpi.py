#!/usr/bin/env python
# -*- coding: utf-8 -*-
# written by Christoph Federrath, 2025

try:
    from mpi4py import MPI
    have_mpi = True
except ImportError:
    MPI = None
    have_mpi = False

# set basic MPI data
if have_mpi:
    comm = MPI.COMM_WORLD  # MPI communicator
    nPE  = comm.Get_size() # get number of MPI ranks
    myPE = comm.Get_rank() # get this MPI rank's number
else:
    comm = None
    nPE  = 1
    myPE = 0


# mpi4pi demo test
def mpi4py_test():

    import argparse
    from cfpack import print, stop
    import cfpack as cfp

    if not MPI:
        print("mpi4py does not appear to be installed.", error=True)

    # parse script arguments
    parser = argparse.ArgumentParser(description='Python MPI (mpi4py) demo.')
    parser.add_argument("-t", "--type", choices=["sum", "send-recv"], default="sum",
                        help='Select MPI demo type.')
    parser.add_argument("-n", "--numbers", type=float, default=1e8,
                        help='Max integer to sum up to [0...n]')
    args = parser.parse_args()

    # get MPI ranks
    comm = MPI.COMM_WORLD
    nPE = comm.Get_size()
    myPE = comm.Get_rank()
    print("Total number of MPI ranks = "+str(nPE))
    comm.Barrier()

    # === MPI summation (allreduce) demo
    if args.type == 'sum':

        # define n and local, global arrays
        n = int(args.numbers)

        # start a new timer
        timer = cfp.timer('mpi4py test')

        # === domain decomposition ===
        mod = n % nPE
        div = n // nPE
        if mod != 0: # Why do this? ...
            div += 1
        print("domain decomposition mod, div = "+str(mod)+", "+str(div))
        my_start =  myPE    * div     # loop start index
        my_end   = (myPE+1) * div - 1 # loop end index
        # last PE gets the rest
        if (myPE == nPE-1): my_end = n
        print("my_start = "+str(my_start)+", my_end = "+str(my_end), mpi=myPE)

        # loop over local chunk of loop to accumulate into sum_local
        sum_local = 0.0
        for i in range(my_start, my_end+1):
            sum_local += i

        print("sum_local = "+str(sum_local), mpi=myPE)

        sum_global = comm.allreduce(sum_local, op=MPI.SUM)

        comm.Barrier()

        print("sum_global = "+str(sum_global))

        # let the timer report
        timer.report()


    # === MPI send-receive demo
    if args.type == 'send-recv':
        if nPE != 2:
            print("Send-receive demo only works with exactly 2 MPI cores.")
            exit(0)
        if myPE == 1:
            # rank 1 sends integer 66
            message = 66
            comm.send(message, dest=0, tag=0)
            print("Message sent: ", message, color='lightred_ex', mpi=myPE)
        if myPE == 0:
            # rank 0 receives
            value = comm.recv(source=1, tag=0)
            print("Message received: ", value, color='green', mpi=myPE)
    return


# ===== the following applies in case we are running this in script mode =====
if __name__ == "__main__":
    mpi4py_test()
