import io
from typing import IO, Any

from docx import Document as DocxDocument
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.oxml.text.run import CT_R
from docx.table import Table
from docx.text.paragraph import Paragraph
from loguru import logger


class DocumentParser:
    def __init__(self, document: DocxDocument):
        """Initialize the DocumentParser with a given .docx document."""
        self.document = document  # Store the document to be parsed
        # Приблизительное количество строк на странице (стандартная страница A4)
        self.lines_per_page = 40
        # Текущая страница
        self.current_page = 1
        # Счетчик строк на текущей странице
        self.lines_on_page = 0
        # Максимальная длина строки в символах
        self.max_line_length = 80

    def parse(self) -> list[dict[str, Any]]:
        """Парсит документ и возвращает список элементов (абзацы, таблицы, изображения) с указанием страницы.

        Returns:
            Список словарей с элементами документа
        """
        result: list[dict[str, Any]] = []
        self.current_page = 1
        self.lines_on_page = 0

        for element in self.document.element.body.iterchildren():
            # Проверяем разрыв страницы
            if self._is_page_break(element):
                self.current_page += 1
                self.lines_on_page = 0
                continue

            if isinstance(element, CT_P):  # Если элемент - абзац
                parsed_paragraph = self.parse_paragraph(
                    Paragraph(element, self.document)
                )
                if not parsed_paragraph:
                    continue

                if isinstance(parsed_paragraph, list):
                    # Обрабатываем список элементов
                    for item in parsed_paragraph:
                        if isinstance(item, dict):
                            item["page"] = self.current_page
                            # Определяем сколько строк занимает элемент
                            content = item.get("content", "")
                            if isinstance(content, str):
                                self._count_lines(content)
                            result.append(item)
                else:
                    # Обрабатываем один элемент
                    parsed_paragraph["page"] = self.current_page
                    # Определяем сколько строк занимает элемент
                    content = parsed_paragraph.get("content", "")
                    if isinstance(content, str):
                        self._count_lines(content)
                    result.append(parsed_paragraph)

            elif isinstance(element, CT_Tbl):  # Если элемент - таблица
                parsed_table = self.parse_table(Table(element, self.document))
                if parsed_table:
                    parsed_table["page"] = self.current_page
                    # Таблица обычно занимает много места
                    rows = len(parsed_table.get("content", []))
                    self.lines_on_page += rows * 2  # Примерная оценка
                    self._check_page_overflow()
                    result.append(parsed_table)

        # Возвращаем результат парсинга с информацией о страницах
        return result

    def _is_page_break(self, element) -> bool:
        """Проверяет, является ли элемент разрывом страницы."""
        return isinstance(element, CT_P) and element.xpath('.//w:br[@w:type="page"]')

    def _count_lines(self, text: str) -> None:
        """Подсчитывает количество строк в тексте и обновляет счетчик строк на странице.
        Если достигается лимит строк на странице, увеличивает номер страницы.
        """
        if not text:
            return

        # Подсчет строк с учетом переносов
        lines = text.count("\n") + 1

        # Дополнительные строки из-за длины текста
        if "\n" not in text:
            lines += len(text) // self.max_line_length

        self.lines_on_page += lines
        self._check_page_overflow()

    def _check_page_overflow(self) -> None:
        """Проверяет, не превышено ли количество строк на странице."""
        if self.lines_on_page >= self.lines_per_page:
            self.current_page += 1
            self.lines_on_page = self.lines_on_page % self.lines_per_page

    def parse_paragraph(
        self, paragraph: Paragraph
    ) -> dict[str, Any] | list[dict[str, Any]] | None:
        """Парсит элемент абзаца.
        Проверяет, содержит ли он графику (изображение или гиперссылку).
        Если содержит графику, обрабатывает ее отдельно.
        Иначе извлекает и возвращает текст абзаца.
        """
        if paragraph._element.xpath(
            ".//a:graphic"
        ):  # Если абзац содержит графический элемент
            return self._parse_child_paragraph(paragraph._element)
        else:
            text = self.get_element_text(paragraph._element)
            if text:
                style_id = paragraph.style.style_id if paragraph.style else "Normal"
                # Определяем, является ли это заголовком
                if style_id.startswith("Heading"):
                    heading_level = (
                        int(style_id.replace("Heading", ""))
                        if style_id != "Heading"
                        else 1
                    )
                    # Форматируем заголовок как в markdown
                    formatted_text = f"{'#' * heading_level} {text}"
                    return {
                        "type": "Text",
                        "content": formatted_text,
                        "style_id": style_id,
                    }
                else:
                    return {"type": "Text", "content": text, "style_id": style_id}
            return None

    def get_element_text(self, element) -> str:
        """Извлекает весь текст из заданного XML-элемента.
        Если элемент содержит текстовые блоки (<w:t>), соединяет их и возвращает результат.
        """
        try:
            children = element.xpath(
                ".//w:t"
            )  # Находит все текстовые элементы внутри заданного элемента
        except Exception as e:
            logger.error(f"Error parsing element: {e}")
            children = (
                element.iterchildren()
            )  # Запасной вариант - перебор детей, если XPath не сработал
        return "".join(c.text for c in children if c.text).strip()

    def _parse_child_paragraph(self, element) -> list[dict[str, Any]]:
        """Парсит дочерний абзац, содержащий либо графику, либо текст.
        Обрабатывает каждый дочерний элемент внутри абзаца, извлекая текст или графическое содержимое.
        """
        data = []
        for child in element.iterchildren():
            if isinstance(child, CT_R) and child.xpath(".//a:graphic"):
                part = self._parse_graphic(child)
            else:
                text = self.get_element_text(child)
                if text:
                    part = {"type": "Text", "content": text}
                else:
                    continue

            if part is None:
                continue
            data.append(part)
        return data

    def _parse_graphic(self, element) -> dict[str, Any]:
        """Парсит графический элемент внутри абзаца.
        Извлекает данные изображения и возвращает их как часть содержимого документа.
        """
        try:
            rid = element.xpath(".//a:blip/@*")[0]
            image_bytes: IO[bytes] = io.BytesIO(
                self.document.part.rels[rid]._target.blob
            )
            return {"type": "Image", "content": image_bytes}
        except Exception as e:
            logger.error(f"Error parsing graphic: {e}")
            return None

    def parse_table(self, table: Table, strip=True) -> dict[str, Any]:
        """Парсит элемент таблицы и возвращает ее данные вместе с объединенными ячейками.
        Аргумент `strip` определяет, нужно ли удалять начальные/конечные пробелы из содержимого ячейки.
        """
        content = [
            [cell.text.strip() if strip else cell.text for cell in row.cells]
            for row in table.rows
        ]

        merged_cells = {}
        for x, row in enumerate(table.rows):
            for y, cell in enumerate(row.cells):
                try:
                    if (
                        hasattr(cell, "_tc")
                        and cell._tc is not None
                        and (cell._tc.vMerge or cell._tc.grid_span != 1)
                    ):
                        tc = (
                            cell._tc.top,
                            cell._tc.bottom,
                            cell._tc.left,
                            cell._tc.right,
                        )
                        merged_cells["_".join(map(str, tc))] = cell.text
                except Exception as e:
                    logger.error(f"Error processing cell at ({x}, {y}): {e}")

        return {"type": "Table", "content": content, "merged_cells": merged_cells}
