#!/usr/bin/env bash

if [ ! -f "/usr/local/bin/codeclimate" ]
then
	curl -L https://github.com/codeclimate/codeclimate/archive/master.tar.gz | tar xvz -C $HOME/
	(cd $HOME/codeclimate-* && sudo make install)
	echo "sudo docker run \
--interactive --tty --rm \
--env CODECLIMATE_CODE="$PWD" \
--volume "$PWD":/code \
--volume /var/run/docker.sock:/var/run/docker.sock \
--volume /tmp/cc:/tmp/cc \
codeclimate/codeclimate analyze" > "codeclimate.sh"
fi

chmod 755  /usr/local/bin/codeclimate

codeclimate engines:install
codeclimate analyze