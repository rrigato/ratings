aws dynamodb list-tables \
--region us-east-1

aws dynamodb query \
 --region us-east-1 \
 --key-condition-expression "RATINGS_OCCURRED_ON = :keyval"  \
 --expression-attribute-values '{":keyval" :{"S": "2023-01-22"}}' \
 --table-name $TABLE_NAME