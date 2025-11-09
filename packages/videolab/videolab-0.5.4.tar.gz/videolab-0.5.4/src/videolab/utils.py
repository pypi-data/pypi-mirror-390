# Copyright (C) 2025 Kian-Meng, Ang
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from pathlib import Path


def generate_output_filename(
    input_file: str, output_file: str | None, suffix: str
) -> Path:
    """
    Generates an output filename based on the input file and a suffix,
    unless an explicit output file is provided.
    """
    if output_file is not None:
        return Path(output_file)

    input_path = Path(input_file)
    return input_path.with_stem(f"{input_path.stem}_{suffix}")
