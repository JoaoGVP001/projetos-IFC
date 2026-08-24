import unittest

from resolvehub_ingestion.policy import classify_entry


class PolicyTests(unittest.TestCase):
    def test_includes_supported_documents(self) -> None:
        decision = classify_entry("Help/Procedimentos/erro-3050.pdf", 10_000)
        self.assertEqual(decision.status, "include")

    def test_blocks_certificate_and_database_files(self) -> None:
        self.assertEqual(classify_entry("Help/certificado.pfx", 5_000).status, "block")
        self.assertEqual(classify_entry("Help/cliente.fdb", 5_000).status, "block")

    def test_blocks_secret_filename_even_when_text(self) -> None:
        decision = classify_entry("Help/Senha - sistema.txt", 200)
        self.assertEqual(decision.status, "block")
        self.assertEqual(decision.reason, "secret_filename")

    def test_blocks_secret_directory_even_when_filename_is_generic(self) -> None:
        decision = classify_entry("Help/Senhas/anotacao.txt", 200)
        self.assertEqual(decision.status, "block")
        self.assertEqual(decision.reason, "secret_filename")

    def test_requires_manual_review_for_sql_and_pii_filename(self) -> None:
        self.assertEqual(classify_entry("Help/correcao.sql", 200).status, "review")
        self.assertEqual(classify_entry("Help/CNPJ.txt", 200).status, "review")

    def test_blocks_path_traversal_and_symlink(self) -> None:
        self.assertEqual(classify_entry("../../segredo.txt", 200).reason, "unsafe_path")
        self.assertEqual(classify_entry("Help/link.txt", 200, is_symlink=True).reason, "symlink")

    def test_defers_images_and_media(self) -> None:
        self.assertEqual(classify_entry("Help/tela.png", 200).status, "defer")
        self.assertEqual(classify_entry("Help/video.mp4", 200).status, "defer")


if __name__ == "__main__":
    unittest.main()
