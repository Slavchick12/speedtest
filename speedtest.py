"""Замер скорости скачивания: N последовательных запросов к URL, средние время и скорость."""

import argparse
import sys
import time
import urllib.error
import urllib.request

CHUNK_SIZE = 64 * 1024
MB = 1024 * 1024


def download(url: str, timeout: float) -> tuple[int, float]:
    """Скачивает url целиком, возвращает (байты, секунды)."""
    request = urllib.request.Request(url, headers={
        'User-Agent': 'speedtest.py',
        'Cache-Control': 'no-cache',
    })
    start, size = time.perf_counter(), 0

    with urllib.request.urlopen(request, timeout=timeout) as response:
        while chunk := response.read(CHUNK_SIZE):
            size += len(chunk)

    return size, time.perf_counter() - start


def main() -> int:
    parser = argparse.ArgumentParser(description='Замер скорости интернета')

    parser.add_argument('url', help='адрес тяжёлого файла, например картинки')
    parser.add_argument('-n', '--requests', type=int, default=10, help='число запросов (по умолчанию 10)')
    parser.add_argument('-t', '--timeout', type=float, default=30, help='таймаут запроса, сек')

    args = parser.parse_args()
    total_bytes, total_time, ok = 0, 0.0, 0

    for i in range(1, args.requests + 1):
        try:
            size, elapsed = download(args.url, args.timeout)
        except (urllib.error.URLError, TimeoutError, ValueError) as e:
            print(f'#{i:>2}: ошибка — {e}', file=sys.stderr)
            continue

        ok += 1
        total_bytes += size
        total_time += elapsed
        print(f'#{i:>2}: {size / MB:.2f} МБ за {elapsed:.3f} с — {size / MB / elapsed:.2f} МБ/с')

    if not ok:
        print('Ни один запрос не прошёл', file=sys.stderr)
        return 1

    speed = total_bytes / MB / total_time

    print()
    print(f'Успешных запросов: {ok} из {args.requests}')
    print(f'Скачано всего:     {total_bytes / MB:.2f} МБ')
    print(f'Среднее время:     {total_time / ok:.3f} с')
    print(f'Скорость:          {speed:.2f} МБ/с ({speed * 8:.1f} Мбит/с)')

    return 0


if __name__ == '__main__':
    sys.exit(main())
