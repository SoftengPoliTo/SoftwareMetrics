TARGET_PATH = ./CC++_Tools
TMP_PATH    = ./.tmp_CC++_Tools
TOOLS_PATH  = ./CC++_Tools_SourceCodes

TOKEI_DEST_PATH = $(TARGET_PATH)/Tokei
TOKEI_TMP_PATH = $(TMP_PATH)/Tokei

CCCC_DEST_PATH = $(TARGET_PATH)/CCCC
CCCC_TMP_PATH = $(TMP_PATH)/CCCC

HALSTEAD_METRICS_DEST_PATH = $(TARGET_PATH)/Halstead_Metrics
HALSTEAD_METRICS_TMP_PATH = $(TMP_PATH)/Halstead_Metrics_tool

#METRIX_PLUSPLUS_DEST_PATH = $(TARGET_PATH)/Metrixpp

#CLIPPY_DEST_PATH = $(TARGET_PATH)/Clippy
#CLIPPY_TMP_PATH = $(TMP_PATH)/Clippy



build: build_tokei build_cccc

target_dir: 
	-mkdir -p $(TMP_PATH)

clean_tmp_dir:
	-rm -r $(TMP_PATH)

clean_target_dir:
	-rm -r $(TARGET_PATH)

clean_all: clean_target_dir clean_tmp_dir



build_tokei: target_dir
	@echo
	@echo Building Tokei...
	cp -r $(TOOLS_PATH)/Tokei $(TOKEI_TMP_PATH)
	cd $(TOKEI_TMP_PATH) && cargo build --release
	# ---  TOKEI  ---

install_local_tokei: build_tokei
	@echo
	-mkdir -p $(TOKEI_DEST_PATH)
	cp $(TOKEI_TMP_PATH)/target/release/tokei $(TOKEI_DEST_PATH)
	# --- QUI ---



build_cccc: target_dir
	@echo 
	@echo Building CCCC...
	cp -r $(TOOLS_PATH)/CCCC/cccc-3.1.4 $(CCCC_TMP_PATH)
	cd $(CCCC_TMP_PATH) && make pccts && make cccc && make test
	# ---  CCCC   ---

install_local_cccc: build_cccc
	@echo
	-mkdir -p $(CCCC_DEST_PATH)
	cp $(CCCC_TMP_PATH)/cccc/cccc $(CCCC_DEST_PATH)



build_halstead_metrics_tool: target_dir
	@echo
	@echo Building Halstead Metrics tool...
	cp -r $(TOOLS_PATH)/Halstead_Metrics_tool $(HALSTEAD_METRICS_TMP_PATH)
	# --- Halstead Metrics tool ---

install_local_halstead_metrics_tool: build_halstead_metrics_tool
	@echo
	-mkdir -p $(HALSTEAD_METRICS_DEST_PATH)
	cp $(HALSTEAD_METRICS_TMP_PATH)/Halstead-Metrics.jar $(HALSTEAD_METRICS_DEST_PATH)
	cp $(HALSTEAD_METRICS_TMP_PATH)/halstead-metrics.sh  $(HALSTEAD_METRICS_DEST_PATH)



#build_metrix_plusplus:
#	@echo
#	@echo Building Metrix Plus Plus...
#	cp -r $(OLD_TOOLS_PATH)/metrixplusplus-1.5.1 $(METRIX_PLUSPLUS_DEST_PATH)
#	chmod +x $(METRIX_PLUSPLUS_DEST_PATH)/metrix++.py
#	chmod +x $(METRIX_PLUSPLUS_DEST_PATH)/metrixpp.py
#	# --- Metrix Plus Plus ---

#build_clippy: target_dir
#	@echo 
#	@echo Building Clippy...
#	cp -r $(TOOLS_PATH)/Rust-Clippy $(CLIPPY_TMP_PATH)
#	cd $(CLIPPY_TMP_PATH) && cargo build
#	# ---  CLIPPY  ---