#!/bin/bash

# Function to get the installed version of a package
get_package_version() {
    local package=$1
    pip show $package 2>/dev/null | grep "Version:" | cut -d " " -f 2
}

# Read requirements.txt line by line
while IFS= read -r line || [[ -n "$line" ]]; do
    # Skip empty lines and comments
    if [[ -z "$line" ]] || [[ "$line" =~ ^#.* ]]; then
        echo "$line"
        continue
    fi

    # Check if line already has version specification
    if [[ "$line" =~ (==|>=|<=|~=) ]]; then
        echo "$line"
    else
        # Get package name (remove any trailing comments)
        package=$(echo "$line" | cut -d "#" -f 1 | tr -d '[:space:]')
        version=$(get_package_version "$package")
        
        if [ ! -z "$version" ]; then
            echo "$package==$version"
        else
            echo "# Warning: Could not find version for $package" >&2
            echo "$line"
        fi
    fi
done < "requirements.txt"