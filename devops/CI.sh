################################
#Miscellaneous AWSCLI commands to setup CI/CD pipeline
################################

 #aws cloudformation execute-change-set --change-set-name
 #<change_set_arn>
aws cloudformation execute-change-set --change-set-name \
<change_set_arn>

aws cloudformation create-stack --stack-name dev-ratings-backend-ratings \
  --template-body file://templates/ratings_backend.yml \
  --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND

  ##allows for much more detailed error logging for stack
  #creation events
aws cloudformation describe-stack-events --stack-name ratings-pipeline \
   > output2.json



