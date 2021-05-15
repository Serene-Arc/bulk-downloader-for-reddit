if [ ! -z "$REDDIT_TOKEN" ]
then
    cp ./bdfr/default_config.cfg ./test_config.cfg
    echo -e "\nuser_token = $REDDIT_TOKEN" >> ./test_config.cfg
fi