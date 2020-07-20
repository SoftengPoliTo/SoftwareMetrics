TARGET_PATH = ./tools
TMP_PATH    = ./.tmp_tools
TOOLS_PATH  = ./tools_source_codes

TOKEI_DEST_PATH = $(TARGET_PATH)/Tokei
TOKEI_TMP_PATH  = $(TMP_PATH)/Tokei

RUST_CODE_ANALYSIS_DEST_PATH = $(TARGET_PATH)/rust-code-analysis
RUST_CODE_ANALYSIS_TMP_PATH  = $(TMP_PATH)/rust-code-analysis

CCCC_DEST_PATH = $(TARGET_PATH)/CCCC
CCCC_TMP_PATH  = $(TMP_PATH)/CCCC

HALSTEAD_METRICS_DEST_PATH = $(TARGET_PATH)/Halstead_Metrics_Tool
HALSTEAD_METRICS_TMP_PATH  = $(TMP_PATH)/Halstead_Metrics_Tool

MAINTAINABILITY_INDEX_DEST_PATH = $(TARGET_PATH)/Maintainability_Index
MAINTAINABILITY_INDEX_TMP_PATH  = $(TMP_PATH)/Maintainability_Index

.PHONY: clean install

target_dir:
	-mkdir -p $(TMP_PATH)
	-mkdir -p $(TARGET_PATH)

clean_tmp_dir:
	-rm -rf $(TMP_PATH)

clean_target_dir:
	-rm -rf $(TARGET_PATH)

clean: clean_target_dir clean_tmp_dir

build_all: build_tokei \
           build_rust_code_analysis \
           build_cccc \
           build_maintainability_index \
           build_halstead_metrics_tool

install: install_tokei \
         install_rust_code_analysis \
         install_cccc \
         install_maintainability_index \
         install_halstead_metrics_tool \


build_rust_code_analysis: target_dir
	@echo
	@echo Building rust-code-analysis...
	cp -r $(TOOLS_PATH)/rust-code-analysis $(RUST_CODE_ANALYSIS_TMP_PATH)
	cd $(RUST_CODE_ANALYSIS_TMP_PATH) && cargo build --workspace --release --all-features
	# ---  RUST_CODE_ANALYSIS  ---

clean_rust_code_analysis:
	rm -rf $(RUST_CODE_ANALYSIS_DEST_PATH) $(RUST_CODE_ANALYSIS_TMP_PATH)

install_rust_code_analysis: build_rust_code_analysis
	@echo
	-mkdir -p $(RUST_CODE_ANALYSIS_DEST_PATH)
	cp $(RUST_CODE_ANALYSIS_TMP_PATH)/target/release/rust-code-analysis-cli \
	   $(RUST_CODE_ANALYSIS_DEST_PATH)



build_tokei: target_dir
	@echo
	@echo Building Tokei...
	cp -r $(TOOLS_PATH)/Tokei $(TOKEI_TMP_PATH)
	cd $(TOKEI_TMP_PATH) && cargo build --release --all-features
	# ---  TOKEI  ---

clean_tokei:
	rm -rf $(TOKEI_DEST_PATH) $(TOKEI_TMP_PATH)

install_tokei: build_tokei
	@echo
	-mkdir -p $(TOKEI_DEST_PATH)
	cp $(TOKEI_TMP_PATH)/target/release/tokei $(TOKEI_DEST_PATH)



build_cccc: target_dir
	@echo 
	@echo Building CCCC...
	cp -r $(TOOLS_PATH)/CCCC $(CCCC_TMP_PATH)
	cd $(CCCC_TMP_PATH)/pccts && make && cd ..
	cd $(CCCC_TMP_PATH) && make cccc && make test
	# ---  CCCC   ---

clean_cccc:
	rm -rf $(CCCC_DEST_PATH) $(CCCC_TMP_PATH)

install_cccc: build_cccc
	@echo
	-mkdir -p $(CCCC_DEST_PATH)
	cp $(CCCC_TMP_PATH)/cccc/cccc $(CCCC_DEST_PATH)



build_halstead_metrics_tool: target_dir
	@echo
	@echo Building Halstead Metrics tool...
	-mkdir $(HALSTEAD_METRICS_TMP_PATH)
	cp $(TOOLS_PATH)/Halstead_Metrics_Tool/Halstead-Metrics.jar \
	   $(HALSTEAD_METRICS_TMP_PATH)/Halstead-Metrics.jar
	# --- Halstead Metrics tool ---

clean_halstead_metrics_tool:
	rm -rf $(HALSTEAD_METRICS_DEST_PATH) $(HALSTEAD_METRICS_TMP_PATH)

install_halstead_metrics_tool: build_halstead_metrics_tool
	@echo
	-mkdir -p $(HALSTEAD_METRICS_DEST_PATH)
	cp $(HALSTEAD_METRICS_TMP_PATH)/Halstead-Metrics.jar \
	   $(HALSTEAD_METRICS_DEST_PATH)



build_maintainability_index: target_dir
	@echo
	@echo Installing dependencies for Maintainability Index tool...
	@echo 'Install dependencies with: "pip install pep8 nose pylint"'

	@echo Building Maintainability Index tool...
	cp -r $(TOOLS_PATH)/Maintainability_Index $(MAINTAINABILITY_INDEX_TMP_PATH)
	# --- Maintainability Index tool ---

clean_maintainability_index:
	rm -rf $(MAINTAINABILITY_INDEX_DEST_PATH) $(MAINTAINABILITY_INDEX_TMP_PATH)

install_maintainability_index: build_maintainability_index
	cp -r $(MAINTAINABILITY_INDEX_TMP_PATH) $(MAINTAINABILITY_INDEX_DEST_PATH)
