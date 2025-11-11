# 🧬 PhyloRun

PhyloRun allows you to run BEAST X, BEAST 2, RevBayes, and LPhy experiments using a single tool.

## 📦 Installation

Use pip to install the CLI tool:

```bash
pip install --upgrade phylorun
```

## 🚀 Features

### Run BEAST X, BEAST 2, RevBayes and LPhy analyses

```bash
phylorun someBeastXModel.xml
phylorun someBeast2Model.xml
phylorun someRevModel.rev
phylorun someRevModel.lphy
```

`phylorun` automatically detects which MCMC engine to use.

By default, `phylorun` tries to use your existing installation of the engine. If this fails, you can specify the location of the binary on your system:

```bash
phylorun --bin "/Applications/BEAST X 10.5.0/bin/beast" someBeastXModel.xml
phylorun --bin "/Applications/BEAST 2.7.7/bin/beast" someBeast2Model.xml
phylorun --bin "/usr/bin/rev" someRevModel.rev
```

If you don't have an engine installed on your local system, you can use the `--container` flag and `phylorun` automatically installs everything that's needed in an isolated environment:

```bash
phylorun --container someBeastXModel.xml
phylorun --container someBeast2Model.xml
phylorun --container someRevModel.rev
```

Currently, this does not work when your BEAST 2 analysis uses packages.

### Run PhyloSpec analyses

`phylorun` can run a PhyloSpec analysis using any of the engines:

```bash
phylorun --engine lphy model.phylospec
```

### Benchmark engines

You can use `phylorun` to see which engine is the fastest for your PhyloSpec model:

```bash
phylorun benchmark model.phylospec
```

### Validate engines

You can use `phylorun` to validate that the engines produce the same results for your PhyloSpec model:

```bash
phylorun validate model.phylospec
```

### Configuration

All unknown arguments are directly passed to the engine (put them at the end of the command):

```bash
phylorun someBeast2Model.xml -resume
```

For LPhy, arguments prefixed with `--beast2` will be passed to BEAST 2 and not to LPhyBeast:

```bash
phylorun someLphyModel.lphy --beast2-resume
```