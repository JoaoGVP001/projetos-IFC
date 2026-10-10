import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from resolvehub_ingestion.catalog import catalog_zip


class CatalogTests(unittest.TestCase):
    def test_catalogs_every_file_and_masks_protected_titles(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            archive_path = Path(directory) / "Help.zip"
            with ZipFile(archive_path, "w") as archive:
                archive.writestr("Help/3- Help Geral/Erro de status.txt", "procedimento")
                archive.writestr("Help/3- Help Geral/cliente 123456789.pdf", "pdf")
                archive.writestr("Help/Senhas/acesso.txt", "segredo")
                archive.writestr("Help/tela.png", "imagem")

            catalog = catalog_zip(archive_path)
            help_items = catalog["items"][:-2]

            self.assertEqual(catalog["archive_files"], 4)
            self.assertEqual(catalog["total_sources"], 6)
            self.assertEqual(help_items[0]["title"], "Erro de status")
            self.assertFalse(help_items[0]["masked_title"])
            self.assertTrue(help_items[1]["masked_title"])
            self.assertEqual(help_items[2]["status"], "block")
            self.assertTrue(help_items[2]["masked_title"])
            self.assertEqual(help_items[3]["status"], "defer")


if __name__ == "__main__":
    unittest.main()
