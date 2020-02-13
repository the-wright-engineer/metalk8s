#!/bin/bash

KUBECONFIG=${KUBECONFIG:-/etc/kubernetes/admin.conf}
STATUS=Running
NAMESPACE=

declare -i SLEEP_TIME=5 \
           RETRY=30

LONG_OPTS=kubeconfig:,namespace:,retry:,sleep-time:,status:
SHORT_OPTS=k:n:r:s:t:

if ! options=$(getopt --options "$SHORT_OPTS" --long "$LONG_OPTS" -- "$@"); then
    echo "Incorrect arguments provided" 1>&2
    exit 1
fi

eval set -- "$options"

while :; do
    case "$1" in
        -k|--kubeconfig)
            KUBECONFIG=$2
            shift
            ;;
        -t|--sleep-time)
            SLEEP_TIME=$2
            shift
            ;;
        -n|--namespace)
            NAMESPACE=--namespace=$2
            shift
            ;;
        -r|--retry)
            RETRY=$2
            shift
            ;;
        -s|--status)
            STATUS=$2
            shift
            ;;
        --)
            shift
            break
            ;;
        *)
            echo "Option parsing failure" 1>&2
            exit 1
            ;;
    esac
    shift
done

[[ $NAMESPACE ]] || NAMESPACE=--all-namespaces

check_pods_status() {
    kubectl get pods "$NAMESPACE" \
        --field-selector="status.phase!=$STATUS" \
        --kubeconfig="$KUBECONFIG" \
        2>&1 | grep 'No resources found' &> /dev/null
}

for ((try = 0; try <= RETRY; ++try)); do
    if ! check_pods_status; then
        echo "Waiting for pods to be $STATUS..."
        sleep "$SLEEP_TIME"
    else
        echo "All pods are $STATUS!"
        exit 0
    fi
done

echo "Pods are still not $STATUS after $RETRY retries in" \
     "$(( RETRY * TIME_TO_SLEEP )) seconds!" 1>&2

exit 1
