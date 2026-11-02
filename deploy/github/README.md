# CI-workflow (nog te activeren)

`test.yml` hoort in `.github/workflows/test.yml`. De token van de server mag geen workflows pushen (geen
`workflow`-scope), daarom staat hij hier. Zolang hij niet op GitHub staat, zijn er geen check-runs en zet
`/usr/local/bin/autodeploy` Synoptikon niet automatisch live.

Activeren (één keer, door Pieter), een van beide:

- op de server: `gh auth refresh -h github.com -s workflow`, daarna
  `git mv deploy/github/test.yml .github/workflows/test.yml && git commit -m "CI" && git push`;
- of op github.com: *Add file* › `.github/workflows/test.yml`, inhoud van `test.yml` hieronder plakken.
