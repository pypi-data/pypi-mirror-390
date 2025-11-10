from src.Bohdan_drivers_report import main
import datetime

def test_calculate_time_correct():
    assert main.calculate_time("12:14:12.054", "12:11:24.067") == datetime.timedelta(minutes=2, seconds=47, microseconds=987000)

def test_calculate_time_incorrect():
    assert main.calculate_time("12:14:12.054", "12:11:24.067") != datetime.timedelta(minutes=3, seconds=57, microseconds=987000)


def test_create_driver_dict():
    assert main.create_driver_dict(r'test_data') == {'DRR': ['Daniel Ricciardo', 'RED BULL RACING TAG HEUER', '02:47.987000']}

def test_create_driver_dict_wrong():
    assert main.create_driver_dict(r'test_data') != {'DRR': ['Daniel Riccirdo', 'RED BULL RACING TAG HEUER', '02:47.987000']}
