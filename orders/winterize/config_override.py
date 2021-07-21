from config import SCHEDULE_NAMES

SCHEDULES = {
    SCHEDULE_NAMES.WINTER: (
        ('scheduler.every().hour.at(":40")', "sbd"),
        ('scheduler.every().hour.at(":45")', "gps"),
        ('scheduler.every().hour.at(":46")', "seabird"),
        ('scheduler.every().hour.at(":47")', "solar"),
        ('scheduler.every().hour.at(":49")', "aquadopp"),
        ('scheduler.every().hour.at(":50")', "crx"),
        ('scheduler.every().hour.at(":52")', "weather"),
        ('scheduler.every().hour.at(":55")', "sbd"),
        ('scheduler.every().day.at("00:00")', "upload"),
        ('scheduler.every().day.at("05:00")', "tps"),
        ('scheduler.every().day.at("06:00")', "camera"),
        ('scheduler.every().day.at("07:00")', "dts"),
        ('scheduler.every().day.at("11:00")', "tps"),
        ('scheduler.every().day.at("12:00")', "upload"),
        ('scheduler.every().day.at("12:00")', "orders"),
        ('scheduler.every().day.at("17:00")', "tps"),
        ('scheduler.every().day.at("18:00")', "upload"),
        ('scheduler.every().day.at("20:00")', "upload"),
        ('scheduler.every().day.at("21:00")', "upload"),
        ('scheduler.every().day.at("22:00")', "upload"),
        ('scheduler.every().day.at("23:00")', "tps"),
    ),
    SCHEDULE_NAMES.SUMMER: (
        ('scheduler.every().hour.at(":40")', "sbd"),
        ('scheduler.every().hour.at(":45")', "gps"),
        ('scheduler.every().hour.at(":46")', "seabird"),
        ('scheduler.every().hour.at(":47")', "solar"),
        ('scheduler.every().hour.at(":49")', "aquadopp"),
        ('scheduler.every().hour.at(":50")', "crx"),
        ('scheduler.every().hour.at(":52")', "weather"),
        ('scheduler.every().hour.at(":55")', "sbd"),
        #
        ('scheduler.every().day.at("00:00")', "upload"),
        #
        #
        #
        ('scheduler.every().day.at("03:00")', "dts"),
        ('scheduler.every().day.at("03:06")', "upload"),
        ('scheduler.every().day.at("04:10")', "camera"),
        ('scheduler.every().day.at("04:15")', "upload"),
        ('scheduler.every().day.at("05:10")', "tps"),
        ('scheduler.every().day.at("06:00")', "upload"),
        #
        ('scheduler.every().day.at("07:00")', "dts"),
        ('scheduler.every().day.at("07:10")', "upload"),
        ('scheduler.every().day.at("08:00")', "upload"),
        ('scheduler.every().day.at("09:00")', "upload"),
        ('scheduler.every().day.at("10:00")', "upload"),
        #
        #
        #
        ('scheduler.every().day.at("11:05")', "dts"),
        ('scheduler.every().day.at("11:10")', "tps"),
        ('scheduler.every().day.at("12:00")', "orders"),
        ('scheduler.every().day.at("12:10")', "camera"),
        ('scheduler.every().day.at("12:15")', "upload"),
        ('scheduler.every().day.at("13:00")', "upload"),
        ('scheduler.every().day.at("14:00")', "upload"),
        #
        #
        ('scheduler.every().day.at("15:00")', "dts"),
        ('scheduler.every().day.at("15:10")', "upload"),
        ('scheduler.every().day.at("16:00")', "upload"),
        #
        ('scheduler.every().day.at("17:10")', "tps"),
        ('scheduler.every().day.at("17:15")', "upload"),
        ('scheduler.every().day.at("18:00")', "upload"),
        #
        ('scheduler.every().day.at("19:00")', "dts"),
        ('scheduler.every().day.at("20:00")', "upload"),
        ('scheduler.every().day.at("20:10")', "camera"),
        ('scheduler.every().day.at("20:15")', "upload"),
        ('scheduler.every().day.at("21:00")', "upload"),
        ('scheduler.every().day.at("22:00")', "upload"),
        #
        #
        ('scheduler.every().day.at("23:00")', "dts"),
        ('scheduler.every().day.at("23:10")', "tps"),
    ),
    SCHEDULE_NAMES.TEST: (
        ("scheduler.every(1).minutes", "seabird"),
        ("scheduler.every(1).minutes", "solar"),
        ("scheduler.every(1).minutes", "aquadopp"),
        ("scheduler.every(1).minutes", "crx"),
        ("scheduler.every(1).minutes", "gps"),
        ("scheduler.every(1).minutes", "weather"),
        ("scheduler.every(1).minutes", "dts"),
        ("scheduler.every(1).minutes", "camera"),
        ("scheduler.every(1).minutes", "tps"),
        ("scheduler.every(1).minutes", "sbd"),
        ("scheduler.every(1).minutes", "upload"),
        ("scheduler.every(1).minutes", "orders"),
        ("scheduler.every(1).minutes", "archive"),
    ),
    SCHEDULE_NAMES.SAFE: (('scheduler.every().day.at("12:00")', "orders"),),
}
