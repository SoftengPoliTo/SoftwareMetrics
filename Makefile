TARGET_PATH = ./OLD_Tools_
OLD_TOOLS_PATH = ./OLD_Tools_SourceCodes
TOKEI_DEST_PATH = $(TARGET_PATH)/Tokei
CLIPPY_DEST_PATH = $(TARGET_PATH)/Clippy
CCCC_DEST_PATH = $(TARGET_PATH)/CCCC
METRIX_PLUSPLUS_DEST_PATH = $(TARGET_PATH)/Metrixpp
HALSTEAD_METRICS_DEST_PATH = $(TARGET_PATH)/Halstead_Metrics_tool

build: build_tokei build_clippy build_cccc

target_dir: 
	-mkdir -p $(TARGET_PATH)

build_tokei: target_dir
	@echo
	@echo Building Tokei...
	cp -r $(OLD_TOOLS_PATH)/Tokei $(TOKEI_DEST_PATH)
	cd $(TOKEI_DEST_PATH) && cargo build
	# ---  TOKEI  ---

build_clippy: target_dir
	@echo 
	@echo Building Clippy...
	cp -r $(OLD_TOOLS_PATH)/Rust-Clippy $(CLIPPY_DEST_PATH)
	cd $(CLIPPY_DEST_PATH) && cargo build
	# ---  CLIPPY  ---

build_cccc: target_dir
	@echo 
	@echo Building CCCC...
	cp -r $(OLD_TOOLS_PATH)/CCCC/cccc-3.1.4 $(CCCC_DEST_PATH)
	cd $(CCCC_DEST_PATH) && make pccts && make cccc && make test
	# ---  CCCC   ---

build_metrix_plusplus:
	@echo
	@echo Building Metrix Plus Plus...
	cp -r $(OLD_TOOLS_PATH)/metrixplusplus-1.5.1 $(METRIX_PLUSPLUS_DEST_PATH)
	chmod +x $(METRIX_PLUSPLUS_DEST_PATH)/metrix++.py
	chmod +x $(METRIX_PLUSPLUS_DEST_PATH)/metrixpp.py
	# --- Metrix Plus Plus ---

build_halstead_metrics_tool: 
	@echo
	@echo Building Halstead Metrics tool...
	cp -r $(OLD_TOOLS_PATH)/Halstead_Metrics_tool $(HALSTEAD_METRICS_DEST_PATH)
	# --- Halstead Metrics tool ---