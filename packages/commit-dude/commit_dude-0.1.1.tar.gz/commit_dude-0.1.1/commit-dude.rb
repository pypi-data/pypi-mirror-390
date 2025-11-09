class CommitDude < Formula
  include Language::Python::Virtualenv

  desc "CLI that generates Conventional Commits from git diffs using LangChain + OpenAI"
  homepage "https://github.com/cassina/commit-dude"
  url "https://files.pythonhosted.org/packages/source/c/commit-dude/commit-dude-0.1.0.tar.gz"
  sha256 "826311cab83d85d86b5ab2631cfbb3ad234aa2d6cd0591e5a030dea41e19e1ca"
  license "MIT"

  depends_on "python@3.13"

  # Main dependencies - Homebrew will resolve the rest automatically
  resource "langchain" do
    url "https://files.pythonhosted.org/packages/2a/b0/5121cdd19cf99e684043f4eae528c893f56bd25e7711d4de89f27832a5f3/langchain-0.3.20.tar.gz"
    sha256 "29ad90488e6865c18b2879b47e17b11fcb6f1c97d44e763872b8d6c2fb2e3e1b"
  end

  resource "langchain-openai" do
    url "https://files.pythonhosted.org/packages/source/l/langchain-openai/langchain_openai-0.2.15.tar.gz"
    sha256 "c0b27b48db7076f57896f722d0757e5d6a3db8fb8bb8b0fa7e3c8edc3e0c0f19"
  end

  resource "click" do
    url "https://files.pythonhosted.org/packages/b9/2e/0090cbf739cee7d23781ad4b89a9894a41538e4fcf4c31dcdd705b78eb8b/click-8.1.8.tar.gz"
    sha256 "ed53c9d8990d83c2a27deae68e4ee337473f6330c040a31d4225c9574d16096a"
  end

  resource "pyperclip" do
    url "https://files.pythonhosted.org/packages/30/23/2f0a3efc4d6a32f3b63cdff36cd398d9701d26cda58e3ab97ac79fb5e60d/pyperclip-1.9.0.tar.gz"
    sha256 "b7de0142ddc81bfc5c7507eea19da920b92252b548b96186caf94a5e2527d310"
  end

  resource "python-dotenv" do
    url "https://files.pythonhosted.org/packages/bc/57/e84d88dfe0aec03b7a2d4327012c1627ab5f03652216c63d49846d7a6c58/python_dotenv-1.0.1.tar.gz"
    sha256 "e324ee90a023d808f1959c46bcbc04446a10ced277783dc6ee09987c37ec10ca"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    system bin/"commit-dude", "--help"
  end
end