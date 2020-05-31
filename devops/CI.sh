################################
#Miscellaneous AWSCLI commands to setup CI/CD pipeline
################################

#Initial project creation setup
aws cloudformation create-stack --stack-name ratings-pipeline \
 --template-body file://templates/code_pipeline.yml \
 --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND



#Creates the CodeBuild and Code Pipeline Cloudformation stack
aws cloudformation create-change-set --stack-name ratings-pipeline \
 --template-body file://templates/.yml \
 --change-set-name CodePipelineAddition \
 --capabilities CAPABILITY_NAMED_IAM
 #aws cloudformation execute-change-set --change-set-name
 #<change_set_arn>
aws cloudformation execute-change-set --change-set-name \
arn:aws:cloudformation:us-east-1:350255258796:changeSet/CodePipelineAddition/2326ac23-8154-49d4-a328-7edc708a2b53

aws cloudformation update-stack --stack-name ratings-pipeline \
 --template-body file://templates/code_pipeline.yml \
 --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND

 aws cloudformation create-stack --stack-name dev-ratings-backend-ratings \
  --template-body file://templates/ratings_backend.yml \
  --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND

  ##allows for much more detailed error logging for stack
  #creation events
   aws cloudformation describe-stack-events --stack-name ratings-pipeline \
   > output2.json




   #static s3 bucket for testing upload code
aws cloudformation create-stack --stack-name dev-backend-logic \
    --template-body file://templates/ratings_backend.yml \
    --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM
