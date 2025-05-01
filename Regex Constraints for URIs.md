### 1. Scheme
- **ABNF** ( §3.1 ):
```
scheme = ALPHA *( ALPHA / DIGIT / "+" / "-" / "." )
```
- **Regex**:
```regex
^[A-Za-z][A-Za-z0-9+.-]*$
```
---

### 2. Userinfo

- **ABNF** ( §3.2.1 ):
```
userinfo = *( unreserved / pct-encoded / sub-delims / ":" )
```
Where

- unreserved = `ALPHA / DIGIT / "-" / "." / "_" / "~"`
- pct-encoded = `"%" HEXDIG HEXDIG`
- sub-delims = `"!" / "$" / "&" / "'" / "(" / ")" / "*" / "+" / "," / ";" / "="`  
- **Regex**:
```regex
^(?:[A-Za-z0-9\-._~]|%[0-9A-Fa-f]{2}|[!$&'()*+,;=]|:)*$
```


---

### 3. Host

- **ABNF** ( §3.2.2 ):
    ```
    host = IP-literal / IPv4address / reg-name
    ```
    **IP‑literal**:
    ```
    IP-literal = "[" ( IPv6address / IPvFuture ) "]"
    ```
    **IPv4address**:
    ```
    IPv4address = dec-octet "." dec-octet "." dec-octet "." dec-octet
    dec-octet   = DIGIT                 ; 0-9
                / %x31-39 DIGIT         ; 10-99
                / "1" 2DIGIT            ; 100-199
                / "2" %x30-34 DIGIT     ; 200-249
                / "25" %x30-35          ; 250-255
    ```
    **reg-name**:
    ```
    reg-name = *( unreserved / pct-encoded / sub-delims )
    ```

| Variant        | Regex                      |
| -------------- | -------------------------- |
| **IP‑literal** | `^\[(?:[0-9A-Fa-f:.]+)\]$` |
| **IPv4**       | `^(?:25[0-5]`              |
| **reg-name**   | `^(?:[A-Za-z0-9-._~]`      |
### 4. Port
```regex
^\d*$
```
### 5. Authority

- **ABNF** ( §3.2 ):
    
    ```
    authority = [ userinfo "@" ] host [ ":" port ]
    ```

- **Regex** (combines userinfo, host, port):
```regex
^(?:(?:[A-Za-z0-9\-._~]|%[0-9A-Fa-f]{2}|[!$&'()*+,;=]|:)+@)?
(?:
  \[(?:[0-9A-Fa-f:.]+)\]                                  # IP-literal
  |
  (?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)
    (?:\.(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)){3}           # IPv4
  |
  (?:[A-Za-z0-9\-._~]|%[0-9A-Fa-f]{2}|[!$&'()*+,;=])*      
- # reg-name
)
(?::\d*)?$
```
---
### 6. Path

There are several path forms; the most common is **path-abempty** (may be empty or begin with “/”):

- **ABNF** ( §3.3 ):
```
path-abempty  = *( "/" segment )
segment       = *pchar
pchar         = unreserved / pct-encoded / sub-delims / ":" / "@"
```
- **Regex**:
```regex
^(?:/
  (?:[A-Za-z0-9\-._~]|%[0-9A-Fa-f]{2}|[!$&'()*+,;=:@])
)*$
```
---
### 7. Query

- **ABNF** ( §3.4 ):
```
query = *( pchar / "/" / "?" )
```
- **Regex**:
```regex
^(?:[A-Za-z0-9\-._~]|%[0-9A-Fa-f]{2}|[!$&'()*+,;=:@\/?])*$
```
---

### 8. Fragment

- **ABNF** ( §3.5 ):
```
fragment = *( pchar / "/" / "?" )
```
- **Regex**:
```regex
^(?:[A-Za-z0-9\-._~]|%[0-9A-Fa-f]{2}|[!$&'()*+,;=:@\/?])*$
```