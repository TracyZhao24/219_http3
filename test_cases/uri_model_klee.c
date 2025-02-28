//Below is a self‐contained C implementation of a simplified URI resolution function, based on the general guidelines from RFC 3986 (URI Generic Syntax) Section 5. It does not rely on any external libraries but uses only standard C library functions. This code illustrates how to parse the base URI and merge it with a relative (query) URI, stripping dot-segments and reconstructing the final result.

/*  
  Simplified URI Resolver in C (no external libraries)

  References:
    - RFC 3986 (particularly Section 5, "Reference Resolution")
    - RFC 3986, Section 3 ("Syntax Components")

  The resolve_uri function below:
    1. Checks if query_uri is absolute (has a scheme).
       - If it is absolute, we return a copy of it.
    2. Otherwise, we parse the base URI into components.
    3. Merge the path from base URI with the relative path from query_uri.
    4. Apply dot-segment removal (handling "." and "..").
    5. Reconstruct the final URI string and return it.

  NOTE: This is a minimal illustration of RFC 3986 reference resolution and 
        does not handle every edge case (e.g., IPv6 host brackets or 
        percent-encoding normalization). However, it demonstrates the 
        core steps required by the relevant RFCs for basic URI resolution.
*/

#include <klee/klee.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* A small structure to hold parsed URI components. */
typedef struct {
    char *scheme;
    char *authority;
    char *path;
    char *query;
    char *fragment;
} uri_components;

/* 
 * Helper function: duplicates a string safely using malloc. 
 * The caller is responsible for freeing the returned pointer.
 */
static char *safe_strdup(const char *src) {
    if (!src) return NULL;
    char *dup = (char *)malloc(strlen(src) + 1);
    if (dup) strcpy(dup, src);
    return dup;
}

/*
 * Helper function: strip trailing newline, if any (optional usage).
 * Provided here in case you wish to read from stdin and test easily.
 */
static void strip_newline(char *str) {
    if (!str) return;
    char *p = strchr(str, '\n');
    if (p) *p = '\0';
}

/*
 * parse_uri: Simplified parser that extracts the main components
 * of a URI as described in RFC 3986. It does not handle every 
 * edge case but captures typical "scheme://authority/path?query#fragment".
 * 
 * Returns a dynamically allocated uri_components struct. The caller 
 * must free each field and the struct itself when done.
 */
static uri_components *parse_uri(const char *uri_str) {
    uri_components *uc = (uri_components *)calloc(1, sizeof(uri_components));
    if (!uc) return NULL;

    if (!uri_str || !*uri_str) {
        return uc; /* empty everything if no input */
    }

    /* Work on a modifiable copy */
    char *tmp = safe_strdup(uri_str);
    char *p = tmp;

    /* ----- SCHEME ----- */
    /* The scheme is everything before the first ':' if followed by "//". */
    char *scheme_end = strstr(p, "://");
    if (scheme_end) {
        *scheme_end = '\0'; 
        uc->scheme = safe_strdup(p);
        p = scheme_end + 3; /* skip past "://" */
    }

    /* ----- AUTHORITY ----- */
    /* The authority is up to the next '/' or '?' or '#' */
    char *auth_start = p;
    char *path_start  = strpbrk(p, "/?#");
    if (path_start) {
        /* authority ends where path begins */
        *path_start = '\0';
        uc->authority = safe_strdup(auth_start);
        p = path_start + 1; /* move to the next character after '/' (if it is '/') */
    } else {
        /* no '/', '?', or '#' => all is authority */
        uc->authority = safe_strdup(auth_start);
        /* done, no path, query, or fragment */
        free(tmp);
        return uc;
    }

    /* If we encountered a '/', we are now at path_start + 1 in p,
       but we need to adjust if path_start was actually '?' or '#'. 
       In that case, path is empty. */
    if (*(path_start) == '/') {
        /* normal path scenario */
    } else {
        /* means path_start was '?' or '#' => path is empty */
        p--; /* step back so that p points to '?' or '#' next */
    }

    /* ----- PATH ----- */
    {
        char *query_start = strchr(p, '?');
        char *frag_start  = strchr(p, '#');
        /* If we have both '?' and '#', pick whichever comes first. */
        char *cut_point = NULL;
        if (query_start && frag_start) {
            cut_point = (query_start < frag_start ? query_start : frag_start);
        } else if (query_start) {
            cut_point = query_start;
        } else if (frag_start) {
            cut_point = frag_start;
        }

        if (cut_point) {
            /* path ends at cut_point */
            *cut_point = '\0';
            uc->path = safe_strdup(p);
            /* Move p to the character after cut_point. */
            p = cut_point + 1;
            if (cut_point == query_start) {
                /* Query is next, might also contain '#' later. */
                frag_start = strchr(p, '#');
                if (frag_start) {
                    *frag_start = '\0';
                    uc->query = safe_strdup(p);
                    uc->fragment = safe_strdup(frag_start + 1);
                } else {
                    uc->query = safe_strdup(p);
                }
            } else {
                /* We hit a '#' directly. No query, only a fragment. */
                uc->fragment = safe_strdup(p);
            }
        } else {
            /* no query or fragment => entire remainder is path */
            uc->path = safe_strdup(p);
            p += strlen(p);
        }
    }

    free(tmp);
    return uc;
}

/*
 * remove_dot_segments: Implements the dot-segment removal algorithm from
 * RFC 3986, Section 5.2.4
 *
 * It modifies the input path in-place, removing any "." or ".." segments
 * according to the standard rules. Returns a pointer to the cleaned string.
 *
 * For simplicity, we do it in a separate buffer using a copy, then 
 * move the result back.
 */
static char *remove_dot_segments(char *path) {
    if (!path) return NULL;

    char *input = safe_strdup(path);
    char *output = (char *)calloc(strlen(path) + 1, sizeof(char));
    if (!input || !output) {
        free(input);
        free(output);
        return path; /* fallback, though memory might be tight */
    }

    char *read_ptr = input;
    char *write_ptr = output;

    while (*read_ptr != '\0') {
        /* 1. If path starts with "../" or "./" or is exactly "." or ".."
              handle them. Follow the pseudo-code from RFC 3986, Section 5.2.4. */
        if (strncmp(read_ptr, "../", 3) == 0) {
            /* Remove the leading "../" => skip it */
            read_ptr += 3;
        } else if (strncmp(read_ptr, "./", 2) == 0) {
            /* Remove the leading "./" */
            read_ptr += 2;
        } else if (strcmp(read_ptr, "..") == 0) {
            /* Remove last segment in output, if any */
            /* Find last '/' in output */
            char *last_slash = strrchr(output, '/');
            if (last_slash) {
                *last_slash = '\0';
                write_ptr = last_slash;
            } else {
                /* no slash => clear output completely */
                *output = '\0';
                write_ptr = output;
            }
            read_ptr += 2;
        } else if (strcmp(read_ptr, ".") == 0) {
            /* just remove the "." => do nothing essentially except skip it */
            read_ptr += 1;
        } else {
            /* 2. Move one segment from input to output */
            /* The segment is up to the next '/' or end of string */
            char *slash = strchr(read_ptr, '/');
            if (!slash) {
                /* no more slashes => copy the rest and done */
                strcpy(write_ptr, read_ptr);
                read_ptr += strlen(read_ptr);
                write_ptr += strlen(write_ptr);
            } else {
                /* copy including the slash */
                size_t seg_len = slash - read_ptr + 1; 
                strncpy(write_ptr, read_ptr, seg_len);
                write_ptr[seg_len] = '\0';
                read_ptr += seg_len;
                write_ptr += seg_len;
            }
        }
    }

    /* Output is now the cleaned path. Copy it back to path. */
    strcpy(path, output);
    free(input);
    free(output);
    return path;
}

/*
 * merge_paths_from_base: merges the query path into the base path 
 * according to RFC 3986 Section 5.2.3
 *
 * This handles the two main cases:
 *   - If the query path begins with "/", we replace the base path entirely.
 *   - Otherwise, we remove the last segment of the base path and append 
 *     the query path.
 *
 * The result is returned in a newly allocated string. The caller must free it.
 */
static char *merge_paths_from_base(const char *base_path, const char *ref_path) {
    /* If ref_path starts with '/', return ref_path as the new path. */
    if (ref_path && ref_path[0] == '/') {
        return safe_strdup(ref_path);
    }

    /* Otherwise, form a new path by combining base_path with ref_path,
       minus the last segment of base_path. */
    char *merged = NULL;
    if (!base_path || !*base_path) {
        /* If base path is empty or NULL, just use ref_path. */
        merged = safe_strdup(ref_path ? ref_path : "");
        return merged;
    }

    /* We'll copy base_path, remove last segment (anything after final '/'). */
    char *temp = safe_strdup(base_path);
    char *last_slash = strrchr(temp, '/');
    if (last_slash) {
        /* keep the slash in place to append the next segment easily */
        *(last_slash + 1) = '\0';
    } else {
        /* no slash => path is a single segment or empty; wipe it out */
        *temp = '\0';
    }

    /* Now append ref_path (if any) to temp. */
    size_t needed = strlen(temp) + (ref_path ? strlen(ref_path) : 0) + 1;
    merged = (char *)malloc(needed);
    if (!merged) {
        free(temp);
        return NULL;
    }
    snprintf(merged, needed, "%s%s", temp, ref_path ? ref_path : "");
    free(temp);
    return merged;
}

/*
 * build_uri_string: Allocates and constructs the final URI string from 
 * the components (scheme, authority, path, query, fragment).
 *
 * The caller is responsible for freeing the returned string.
 */
static char *build_uri_string(const uri_components *uc) {
    /* scheme://authority/path?query#fragment */
    /* We'll build piece by piece, only if each is nonempty. */

    /* Calculate needed buffer length. Add space for "://", '/', '?', '#', etc. */
    size_t len = 0;
    if (uc->scheme && *uc->scheme) {
        len += strlen(uc->scheme) + 3; /* "://" */
    }
    if (uc->authority && *uc->authority) {
        len += strlen(uc->authority);
    }
    if (uc->path && *uc->path) {
        /* if path doesn't start with '/', we add one if we have authority */
        if (uc->authority && *uc->authority && uc->path[0] != '/') {
            len += 1; /* the slash */
        }
        len += strlen(uc->path);
    }
    if (uc->query && *uc->query) {
        len += 1 + strlen(uc->query); /* '?' + query */
    }
    if (uc->fragment && *uc->fragment) {
        len += 1 + strlen(uc->fragment); /* '#' + fragment */
    }

    char *result = (char *)calloc(len + 1, sizeof(char));
    if (!result) return NULL;

    /* Now build the string */
    if (uc->scheme && *uc->scheme) {
        strcat(result, uc->scheme);
        strcat(result, "://");
    }
    if (uc->authority && *uc->authority) {
        strcat(result, uc->authority);
    }
    if (uc->path && *uc->path) {
        /* Insert a slash if authority is present and path doesn't begin with '/' */
        if (uc->authority && *uc->authority && uc->path[0] != '/') {
            strcat(result, "/");
        }
        strcat(result, uc->path);
    }
    if (uc->query && *uc->query) {
        strcat(result, "?");
        strcat(result, uc->query);
    }
    if (uc->fragment && *uc->fragment) {
        strcat(result, "#");
        strcat(result, uc->fragment);
    }

    return result;
}

/*
 * resolve_uri: Resolves a query_uri relative to a base_uri according to 
 * RFC 3986 Section 5 ("Reference Resolution"). Returns a newly allocated 
 * string containing the resolved URI. The caller is responsible for freeing 
 * the returned pointer.
 *
 * Steps (simplified):
 *   1) If query_uri has a scheme (i.e., "something://"), it's absolute. Return it.
 *   2) Otherwise:
 *      - Parse base_uri into components (scheme, authority, path, query, fragment).
 *      - Parse query_uri into components (check for authority, path, query, fragment).
 *      - Apply the merging rules:
 *         a) If query_uri has authority set, use that path, else merge paths.
 *         b) Remove dot segments from the final path.
 *         c) If query_uri has a query component, use that. Otherwise, if not, keep base's query.
 *         d) Fragments always come from the query_uri unless query_uri fragment is empty.
 *      - Generate the final string from merged components.
 */
char *resolve_uri(char *query_uri) 
{
    char *base_uri = "http://a.a/a"; /* Example base URI */

    /* Edge cases: if base_uri is NULL or empty, or query_uri is NULL */
    if (!base_uri) base_uri = "";
    if (!query_uri) query_uri = "";

    /* 1) Check if query_uri is absolute by looking for "://" */
    /*    (This is a naive check; a more thorough check would detect actual scheme chars). */
    if (strstr(query_uri, "://")) {
        /* It's absolute => return copy of query_uri as is */
        return safe_strdup(query_uri);
    }

    /* 2) Parse base URI and query URI. */
    uri_components *base = parse_uri(base_uri);
    uri_components *ref  = parse_uri(query_uri);

    /* If the query has a scheme, it overrides everything (simplified approach). */
    /* This step is typically overshadowed by the earlier ":// check," but let's be thorough. */
    if (ref->scheme && *ref->scheme) {
        /* This would be an absolute URI. Return a build of ref only. */
        char *result = build_uri_string(ref);
        /* Cleanup */
        free(base->scheme);    free(base->authority); 
        free(base->path);      free(base->query);
        free(base->fragment);  free(base);

        free(ref->scheme);     free(ref->authority); 
        free(ref->path);       free(ref->query);
        free(ref->fragment);   free(ref);

        return result;
    }

    /* Merge scheme */
    if (!ref->scheme || !*ref->scheme) {
        /* Use base's scheme */
        if (base->scheme) {
            ref->scheme = safe_strdup(base->scheme);
        }
    }

    /* Merge authority and path */
    if (ref->authority && *ref->authority) {
        /* If ref has an authority, path is used as is (after dot-segment removal below). */
    } else {
        /* Use base's authority if none in ref */
        free(ref->authority);
        ref->authority = base->authority ? safe_strdup(base->authority) : NULL;

        /* Merge the path */
        char *merged_path = merge_paths_from_base(
                                base->path ? base->path : "",
                                ref->path ? ref->path : "");
        free(ref->path);
        ref->path = merged_path;
    }

    /* Remove dot segments */
    if (ref->path) {
        remove_dot_segments(ref->path);
    }

    /* Merge query if ref does not specify one */
    if (!ref->query || !*ref->query) {
        if (base->query && *base->query) {
            ref->query = safe_strdup(base->query);
        }
    }

    /* The fragment always comes from ref (even if empty, it overrides). */

    /* Build final URI string */
    char *resolved = build_uri_string(ref);

    /* Cleanup memory */
    free(base->scheme);    free(base->authority); 
    free(base->path);      free(base->query);
    free(base->fragment);  free(base);

    free(ref->scheme);     free(ref->authority); 
    free(ref->path);       free(ref->query);
    free(ref->fragment);   free(ref);

    return resolved;
}

int main() {
    char uri[7];

    char x0;
    char x1;
    char x2;
    char x3;
    char x4;
    char x5;

    klee_make_symbolic(&x0, sizeof(x0), "x0");
    klee_make_symbolic(&x1, sizeof(x1), "x1");
    klee_make_symbolic(&x2, sizeof(x2), "x2");
    klee_make_symbolic(&x3, sizeof(x3), "x3");
    klee_make_symbolic(&x4, sizeof(x4), "x4");
    klee_make_symbolic(&x5, sizeof(x5), "x5");

    uri[0] = x0;
    uri[1] = x1;
    uri[2] = x2;
    uri[3] = x3;
    uri[4] = x4;
    uri[5] = x5;
    uri[6] = '\0'; 

    resolve_uri(uri);

    return 0;
}

/* 
   Example main() for quick demo:

   int main() {
       char base[256], query[256];
       printf("Base URI: ");
       fgets(base, 256, stdin);
       strip_newline(base);

       printf("Query (Relative) URI: ");
       fgets(query, 256, stdin);
       strip_newline(query);

       char *final = resolve_uri(base, query);
       printf("Resolved URI: %s\n", final ? final : "(null)");

       free(final);
       return 0;
   }
*/
/*
-----------------------------------

Explanation of main steps:

1) We first check if the query_uri is absolute by looking for “://” (naive but commonly sufficient).  
   • If found, return a copy of query_uri.

2) Otherwise, parse both base and query URIs into their components: scheme, authority, path, query, fragment.

3) Merge according to RFC 3986 Section 5.2.3:  
   • If the query_uri has an authority part, it overrides the base’s authority.  
   • If not, we reuse the base’s authority and merge the paths (remove the base path’s last segment, then append the query path).  
   • Handle dot-segment removal (RFC 3986 Section 5.2.4).  
   • Inherit the query from the base if the query_uri did not explicitly have one.  
   • Fragments always come from the query URI (even if empty).

4) Rebuild into a final URI string and return it.  

This should suffice for a straightforward “resolve_uri” function in pure C without external libraries. Remember that this code is a simplified demonstration and may need further adjustments for production use or for very strict compliance with all URI edge cases.
*/