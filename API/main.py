        raise HTTPException(status_code=400, detail=ERROR_INVALID_REPO_NAME)

    if not file.filename or Path(file.filename).stem != repo_name:
        raise HTTPException(status_code=400, detail=ERROR_REPO_NAME_MISMATCH)

    with zipfile.ZipFile(file.file, "r") as zf:
        buffer_dir = Path(
            os.path.join(tempfile.gettempdir(), TEMP_DIR_PREFIX + repo_name)
        )

        print(zf.infolist())

        if sum(i.file_size for i in zf.infolist()) > MAX_TOTAL_UPLOAD_SIZE:
            shutil.rmtree(buffer_dir, ignore_errors=True)