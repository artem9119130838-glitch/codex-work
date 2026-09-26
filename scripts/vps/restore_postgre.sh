#!/bin/sh


if ! [ ${1} ]
then
{
    echo "No parameter";
    break;
}
elif  [ -d ${1} ];
then
{
    backup_name=${1}
    postgres_path="/opt/pgpro/std-14/bin/"
    psql_cmd="${postgres_path}psql -U postgres"
    pgrestore_cmd="${postgres_path}pg_restore -U postgres --format=d --jobs=4 --verbose"
    new_database_name="unf_restored"

    clear
    ${postgres_path}createdb -U postgres -T template1 ${new_database_name} \
    && ${pgrestore_cmd} --dbname=${new_database_name} ${backup_name}
    echo '\l+' | ${psql_cmd} -d postgres
    echo '\dt' | ${psql_cmd} -d ${new_database_name}
}

else 
{
    echo "Backup directory ${1} not found"
}
fi