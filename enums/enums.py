
import enum


class City(enum.Enum):
    mykolaiv = "mykolaiv"


class Queue(enum.Enum):
    q1_1 = "1.1"
    q1_2 = "1.2"
    q2_1 = "2.1"
    q2_2 = "2.2"
    q3_1 = "3.1"
    q3_2 = "3.2"
    q4_1 = "4.1"
    q4_2 = "4.2"
    q5_1 = "5.1"
    q5_2 = "5.2"
    q6_1 = "6.1"
    q6_2 = "6.2"
    q7_1 = "7.1"
    q7_2 = "7.2"
    q8_1 = "8.1"
    q8_2 = "8.2"
    q9_1 = "9.1"
    q9_2 = "9.2"
    q10_1 = "10.1"
    q10_2 = "10.2"


class Language(enum.Enum):
    ru = "ru"
    uk = "uk"


class ScheduleDelivery(enum.Enum):
    received = "received"
    pending = "pending"
    sent = "sent"


class ScheduleStatus(enum.Enum):
    on = "on"
    off = "off"
    probably = "probably"
    emergency = "emergency"
