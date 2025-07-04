defmodule Pipeline.MixProject do
  use Mix.Project

  def project do
    [
      app: :pipeline,
      version: "0.1.0",
      elixir: "~> 1.18",
      start_permanent: Mix.env() == :prod,
      deps: deps()
    ]
  end

  # Run "mix help compile.app" to learn about applications.
  def application do
    [
      extra_applications: [:logger]
    ]
  end

  # Run "mix help deps" to learn about dependencies.
  defp deps do
    [
      {:instructor_lite, "~> 1.0.0"},
      {:claude_code_sdk, path: "../../claude_code_sdk_elixir"},
      {:yaml_elixir, "~> 2.11"},
      {:jason, "~> 1.4"},
      {:nimble_options, "~> 1.1"},
      {:req, "~> 0.5"},
      {:ecto, "~> 3.12"}
    ]
  end
end
