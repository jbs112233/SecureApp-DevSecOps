# Deployment Runbook

# PreReqs
1. Make sure Docker is running
2. Check the repo to make sure it is ready to go
3. Look over Docker and Alembic migration files
4. Assure database volume is available

# Steps: 
1. Build the docker image
2. Create a consitent database volume
3. Apply the migrations
4. Verify the edits
5. Start the API
6. Verify health
7. Stop the container to avoid errors

