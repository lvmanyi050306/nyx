Nyx Scientific Visualization Project

Project structure:
- data/raw: raw Nyx .dat files, named 0000.dat to 0099.dat. These files are not included in the submission package because of their size; place the course-provided raw data here before rerunning the full pipeline.
- data/processed: generated statistics, threshold tables, and structure metrics.
- code: MATLAB scripts for data checking, statistics, rendering, histograms, and high-density selection.
- results: generated figures grouped by task.
- report: technical report and answer sheet.
- video: demonstration video.
- final_submit: final compressed submission package.

Recommended MATLAB entry point:
1. Open MATLAB in this project root.
2. Put the 100 raw files under data/raw as 0000.dat ... 0099.dat.
3. Run code/main.m.
4. Run interactive_dashboard(fullfile(pwd, "data", "raw"), "0099") for linked brushing.

Recommended Python utilities:
1. Run python code/create_visual_story.py to rebuild static story figures and the video. If raw data is absent, the script rebuilds static story figures from existing results and skips video regeneration.
2. Run python code/create_report.py and python code/create_pdf.py to rebuild DOCX/PDF reports from the latest CSV and figures.
3. Run python code/package_submission.py to rebuild final_submit/学号_姓名_Nyx科学可视化.zip with the expected directory layout.

Multi-software workflow:
- MATLAB R2024b: reads Nyx float32 little-endian volumes, computes statistics, renders volumes and histograms, and opens the linked brushing dashboard.
- Python: combines MATLAB outputs into story images, creates DOCX/PDF reports, computes extra structure metrics, and prepares video frames.
- FFmpeg: encodes the 100-frame evolution storyboard into video/demo.mp4.

Task coverage:
- Volume rendering, transfer function, and lighting: report section 4; code/step4_volume_render.m; results/02_volume_render; transfer_function_design.png.
- Evolution feature summary: report sections 5 and 9; cosmic_web_atlas.png; video/demo.mp4.
- 100-step density statistics and log histograms: report section 6; density_stats.csv; structure_metrics.csv; histogram_temporal_heatmap.png.
- Phase-space linked brushing and high-density selection: report section 7; code/interactive_dashboard.m; results/05_interaction_selection; interaction_storyboard.png.

Important generated assets:
- results/07_visual_story/cosmic_web_atlas.png
- results/07_visual_story/histogram_temporal_heatmap.png
- results/07_visual_story/structure_metrics_dashboard.png
- results/07_visual_story/transfer_function_design.png
- results/07_visual_story/interaction_storyboard.png
- video/demo.mp4

Submission note:
- The zip intentionally excludes data/raw and video/frames.
- The zip preserves code/, data/processed/, results/, report/, video/demo.mp4, README.txt, and 任务要求.txt.
