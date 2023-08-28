from lib.gps import GPS


if __name__ == "__main__":
    gps = GPS()

    gps.initialize()
    print("")
    print(gps.get_coords())