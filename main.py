from analysis import find_GRBs

if __name__ == "__main__":
    # possible satellites:
    ## avion
    ## monitor2
    ## monitor3
    ## monitor4
    ## utmn2
    
    satellite = "avion"
    find_GRBs(satellite, '2023-08-01 00:00:01', '2023-08-31 23:59:59')
    find_GRBs(satellite, '2023-09-01 00:00:01', '2023-09-30 23:59:59')
    find_GRBs(satellite, '2023-10-01 00:00:01', '2023-10-31 23:59:59')
    find_GRBs(satellite, '2023-11-01 00:00:01', '2023-11-30 23:59:59')
    find_GRBs(satellite, '2023-12-01 00:00:01', '2023-12-31 23:59:59')
    find_GRBs(satellite, '2024-01-01 00:00:01', '2024-01-31 23:59:59')
    # find_GRBs(satellite, '2024-02-01 00:00:01', '2024-02-29 23:59:59')