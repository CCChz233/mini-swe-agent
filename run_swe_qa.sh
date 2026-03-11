PYTHONPATH=src python -m minisweagent.run_swe_qa \
  --mode tools_radar \
  --tools-prompt neutral \
  --tool-config swe_qa_bench/config/file_radar_search.yaml \
  --method miniswe_tools_radar \
  --workers 4 \
  --redo-existing
  
PYTHONPATH=src python -m minisweagent.run_swe_qa \
  --mode bash \
  --workers 4 \
  --redo-existing
  
PYTHONPATH=src python -m minisweagent.run_swe_qa \
  --mode tools \
  --workers 4 \
  --redo-existing
  

  



