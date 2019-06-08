# Cronjob has no HOME, so wont find e.g. .netrc file
HOME=/
export HOME

/mnt/sked_tasks/upload_chunks.sh /mnt/grs/tpsfilelist > /mnt/logs/upload_chunks_tps.log
