#!/bin/bash

ATTEMPTS=0
declare -a GET_COLUMN_VALUE=(
    sudo kubectl --kubeconfig "${KUBECONFIG}" get "${RESOURCE_TYPE}"
    "${RESOURCE_NAME}" -n "${NAMESPACE}" -o "custom-columns=${RESOURCE_COLUMN}"
)
CURRENT_VALUE=$("${GET_COLUMN_VALUE[@]}")
until [ "${CURRENT_VALUE}" -eq "${RESOURCE_VALUE}" ]; do
    (( ATTEMPTS++ ))
    if [ "${ATTEMPTS}" -eq "${RETRIES}" ]; then
    echo "${RESOURCE_COLUMN} still not equal to ${RESOURCE_VALUE} after ${ATTEMPTS} attempts" >&2
    exit 1
    fi
    sleep "${SLEEP}"
    CURRENT_VALUE=$("${GET_COLUMN_VALUE[@]}")
done