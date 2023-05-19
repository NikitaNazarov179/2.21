#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sqlite3
import typing as t
from pathlib import Path


def display_reys(re: t.List[t.Dict[str, t.Any]]) -> None:
    """
    Отобразить список рейсов.
    """
    # Проверить, что список рейсов не пуст.
    if re:
        line = '+-{}-+-{}-+-{}-+-{}-+'.format(
            '-' * 4,
            '-' * 30,
            '-' * 20,

            '-' * 8
        )
        print(line)
        print(
            '| {:^4} | {:^30} | {:^20} | {:^8} |'.format(
                "No",
                "Пункт назначения",
                "Номер рейса",
                "Тип"
            )
        )
        print(line)

        # Вывести данные о всех рейсах.
        for idx, rey in enumerate(re, 1):
            print(
                '| {:>4} | {:<30} | {:<20} | {:>8} |'.format(
                    idx,
                    rey.get('pynkt', ''),
                    rey.get('numb', ''),
                    rey.get('samolet', 0)
                )
            )
            print(line)

    else:
        print("Список рейсов пуст.")


def create_db(database_path: Path) -> None:
    """
    Создать базу данных.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Создать таблицу с информацией о рейсах.
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            post_id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_title TEXT NOT NULL
        )
        """
    )

    # Создать таблицу с информацией о рейсах.
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS workers (
            worker_id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_name TEXT NOT NULL,
            post_id INTEGER NOT NULL,

            worker_year INTEGER NOT NULL,
            FOREIGN KEY(post_id) REFERENCES posts(post_id)
        )
        """
    )

    conn.close()


def get_reys(
        database_path: Path,
        pynkt: str,
        numb: int,
        samolet: str
) -> None:
    """
    Добавить рейсы в базу данных.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT post_id FROM posts WHERE pynkt = ?
        """,
        (pynkt,)
    )
    row = cursor.fetchone()
    if row is None:
        cursor.execute(
            """
            INSERT INTO posts (pynkt) VALUES (?)
            """,
            (pynkt,)
        )
        post_id = cursor.lastrowid

    else:
        post_id = row[0]

    # Добавить информацию о новом рейсе.
    cursor.execute(
        """
        INSERT INTO workers (pynkt, numb, samolet)
        VALUES (?, ?, ?)
        """,
        (post_id, numb, samolet)
    )

    conn.commit()
    conn.close()


def select_all(database_path: Path) -> t.List[t.Dict[str, t.Any]]:
    """
    Выбрать все рейсы.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT workers.worker_name, posts.post_title, workers.worker_year
        FROM workers
        INNER JOIN posts ON posts.post_id = workers.post_id
        """
    )
    rows = cursor.fetchall()

    conn.close()
    return [
        {
            "pynkt": row[0],
            "numb": row[1],
            "samolet": row[2],
        }
        for row in rows
    ]


def select_by_pynkt(
        database_path: Path, jet: str
) -> t.List[t.Dict[str, t.Any]]:
    """
    Выбрать самолеты с заданным пунктом.
    """

    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 
        """,
        (jet,)
    )
    rows = cursor.fetchall()

    conn.close()
    return [
        {
            "pynkt": row[0],
            "numb": row[1],
            "samolet": row[2],
        }
        for row in rows
    ]


def main(command_line=None):
    # Создать родительский парсер для определения имени файла.
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "--db",
        action="store",
        required=False,
        default=str(Path.home() / "reys.db"),
        help="The database file name"
    )

    # Создать основной парсер командной строки.
    parser = argparse.ArgumentParser("reys")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )

    subparsers = parser.add_subparsers(dest="command")

    # Создать субпарсер для добавления рейса.
    add = subparsers.add_parser(
        "add",
        parents=[file_parser],
        help="Add a new worker"
    )
    add.add_argument(
        "-p",
        "--pynkt",
        action="store",
        required=True,
        help="The pynkt"
    )
    add.add_argument(
        "-n",
        "--numb",
        action="store",
        help="The number reys"
    )
    add.add_argument(
        "-s",
        "--samolet",
        action="store",
        type=int,
        required=True,
        help="The type samolet"
    )

    # Создать субпарсер для отображения всех рейсов.
    _ = subparsers.add_parser(
        "display",
        parents=[file_parser],
        help="Display all reys"
    )

    # Создать субпарсер для выбора рейсов.
    select = subparsers.add_parser(
        "select",
        parents=[file_parser],
        help="Select the reys"
    )
    select.add_argument(
        "-P",
        "--pynkt",
        action="store",
        required=True,
        help="The required pynkt"
    )

    # Выполнить разбор аргументов командной строки.
    args = parser.parse_args(command_line)

    # Получить путь к файлу базы данных.
    db_path = Path(args.db)
    create_db(db_path)

    # Добавить рейс.
    if args.command == "add":
        get_reys(db_path, args.pynkt, args.numb, args.samolet)

    # Отобразить все рейсы.
    elif args.command == "display":
        display_reys(select_all(db_path))

    # Выбрать требуемые рейсы.
    elif args.command == "select":
        display_reys(select_by_pynkt(db_path, args.pynkt))
        pass


if __name__ == "__main__":
    main()
