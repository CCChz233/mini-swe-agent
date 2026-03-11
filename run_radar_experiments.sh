PYTHONPATH=src python -m minisweagent.run_locbench \
  --mode tools_radar \
  --tools-prompt neutral \
  --tool-config locbench/config/file_radar_search.yaml \
  --method miniswe_tools_radar__legacy__ab \
  --workers 4 \
  --skip-missing \
  --redo-existing

PYTHONPATH=src python -m minisweagent.run_locbench \
  --mode tools_radar \
  --tools-prompt neutral \
  --tool-config locbench/config/file_radar_search_tree_v2.yaml \
  --method miniswe_tools_radar__tree_v2__ab \
  --workers 4 \
  --skip-missing \
  --redo-existing
