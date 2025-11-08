class Alprina < Formula
  desc "AI-powered cybersecurity CLI tool for developers"
  homepage "https://alprina.com"
  url "https://files.pythonhosted.org/packages/source/a/alprina-cli/alprina-cli-0.1.1.tar.gz"
  sha256 "REPLACE_WITH_ACTUAL_SHA256_HASH"
  license "MIT"

  depends_on "python@3.11"

  resource "rich" do
    url "https://files.pythonhosted.org/packages/source/r/rich/rich-13.6.0.tar.gz"
    sha256 "5c14d22737e6d5084ef4771b62d5d4363165b403455a30a1c8ca39dc7b644bef"
  end

  resource "typer" do
    url "https://files.pythonhosted.org/packages/source/t/typer/typer-0.12.3.tar.gz"
    sha256 "49e73131481d804288ef62598d97a1ceef3058905aa536a1134f90891ba35482"
  end

  resource "httpx" do
    url "https://files.pythonhosted.org/packages/source/h/httpx/httpx-0.25.1.tar.gz"
    sha256 "ffd96d5cf901e63863d9f1b4b6807861dbea4d301613415d9e4e57ede6c5ee70"
  end

  resource "pydantic" do
    url "https://files.pythonhosted.org/packages/source/p/pydantic/pydantic-2.5.0.tar.gz"
    sha256 "b9992f636b95b606a1cff82a4538d5a0a8f1d4ba9a5b5e1a4d2b4e1b4e52e44b"
  end

  resource "python-dotenv" do
    url "https://files.pythonhosted.org/packages/source/p/python-dotenv/python-dotenv-1.0.0.tar.gz"
    sha256 "a8df96034aae6d2d50a4ebe8216326c61c3eb64836776504fcca410e5937a3ba"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/alprina", "--version"
    assert_match "Alprina CLI", shell_output("#{bin}/alprina --help")
  end
end