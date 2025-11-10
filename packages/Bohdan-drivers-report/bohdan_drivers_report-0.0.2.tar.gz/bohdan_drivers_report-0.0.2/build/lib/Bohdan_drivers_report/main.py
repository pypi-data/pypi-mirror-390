import datetime
from datetime import timedelta
import argparse

def file_open(path):
    with open(path, "r", encoding="UTF8") as txt:
        content = txt.readlines()
    return content

def read_log(path:str):
    content = file_open(path)

    result = {}
    for line in content:
        a,b = line.split("_")
        a = a[:3]
        result[a] = b.strip()

    return result

def read_txt(path:str):
    content = file_open(path)

    result = {}
    for line in content:
        a,b,c = line.split("_")
        result[a] = [b,c.strip()]
    return result


def calculate_time(start:str, end:str):
    start = datetime.datetime.strptime(start, "%H:%M:%S.%f")
    end = datetime.datetime.strptime(end, "%H:%M:%S.%f")
    if end > start:
        result = end - start
    else:
        result = start - end
    return result


def format_timedelta(td):
    minutes, seconds = divmod(td.seconds + td.days * 86400, 60)
    hours, minutes = divmod(minutes, 60)
    return '{:02d}:{:02d}.{:06d}'.format(minutes, seconds, td.microseconds)

def sort_dict(dct:dict):
    sorted_items = sorted(dct.items(), key=lambda kv: kv[1][2])
    return dict(sorted_items)

def create_driver_dict(files):

    start_path = f"{files}/start.log"
    end_path = f"{files}/end.log"
    abbs_path = f"{files}/abbreviations.txt"

    start_dict = read_log(start_path)
    end_dict = read_log(end_path)
    abbs_dict = read_txt(abbs_path)

    result = {}

    for abb in abbs_dict:
        result[abb] = abbs_dict[abb] + [format_timedelta(calculate_time(start_dict[abb], end_dict[abb]))]

    return result

def build_report(files):

    result = create_driver_dict(files)

    sorted_result = sort_dict(result)

    report = {}

    counter = 1
    for i in sorted_result.values():
        if counter == 16:
            report[" "] = "-"*68
        report[i[0]] = f"{counter}. {i[0]:<17}\t| {i[1]:<25}\t| {i[2]}"
        counter += 1

    return report


def get_args():
    parser = argparse.ArgumentParser(description='Driver output.')
    parser.add_argument('--files', metavar='', nargs='?',
                       help='an integer for the accumulator', default='data/')
    parser.add_argument('--driver', metavar='',
                       help='імя драйвера')
    # parser.parse_args('--asc')

    parser.add_argument("--order", choices=['asc', 'desc'], default='asc',
                        help="Sort order (default is ascending)")

    args = parser.parse_args()
    return args

def print_report():
    args = get_args()
    drivers = build_report(args.files)

    if args.driver:
        driver = args.driver.title()
        print(drivers[driver])
    else:
        if args.order == 'desc':
            for driver in list(drivers.values())[::-1]:
                print(driver)
        else:
            for driver in drivers.values():
                print(driver)


if __name__ == '__main__':
    print_report()


