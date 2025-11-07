class AgeMcpServer < Formula
  include Language::Python::Virtualenv

  desc "Apache AGE MCP Server"
  homepage "https://github.com/rioriost/homebrew-age-mcp-server/"
  url "https://files.pythonhosted.org/packages/cf/c4/2809265de03d52d86780d39689548d8a8bb7868c6d1b6a798dc082fd76b1/age_mcp_server-0.2.30.tar.gz"
  sha256 "0646a09e4712180d3d858a9a9562895a140d12f6739db2efe9366df1ad9c32af"
  license "MIT"

  depends_on "python@3.13"

  resource "agefreighter" do
    url "https://files.pythonhosted.org/packages/df/3d/5f701f1135cef1ced759c319d6f5c0454c379e5e427d4067e20e03017be9/agefreighter-1.0.20.tar.gz"
    sha256 "1a7994b684fe3e91727e632c1883751646bb157b02ff3047f6f73e68912cafd5"
  end

  resource "ply" do
    url "https://files.pythonhosted.org/packages/e5/69/882ee5c9d017149285cab114ebeab373308ef0f874fcdac9beb90e0ac4da/ply-3.11.tar.gz"
    sha256 "00c7c1aaa88358b9c765b6d3000c6eec0ba42abca5351b095321aef446081da3"
  end

  def install
    virtualenv_install_with_resources
    system libexec/"bin/python", "-m", "pip", "install", "psycopg[binary,pool]", "mcp"
  end

  test do
    system "#{bin}/age-mcp-server", "--help"
  end
end
