class Trmd < Formula
  include Language::Python::Virtualenv

  desc "Translate Markdown using OpenAI"
  homepage "https://github.com/rioriost/homebrew-trmd/"
  url "https://files.pythonhosted.org/packages/cf/68/c940bdb75456d2b93a036a1404da675c8c3d36525bc44fc8b82a7020d3f6/trmd-0.1.24.tar.gz"
  sha256 "10758424a9a8f9674a16301d5214cac0dfd21cbbc3fdc62104f3bb54334506e9"
  license "MIT"

  depends_on "python@3.13"

  def install
    virtualenv_install_with_resources
    system libexec/"bin/python", "-m", "pip", "install", "openai"
  end

  test do
    system "#{bin}/trmd", "--help"
  end
end
