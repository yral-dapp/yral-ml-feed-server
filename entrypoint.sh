#!/bin/bash

USERNAME=$1

echo "Inside entrypoint script."
chown $USERNAME:$USERNAME /home/$USERNAME

echo "About to run post-initialization script as $USERNAME."
su -c "bash ./post-initialization.sh" $USERNAME
