---
name: apple-contacts
description: Look up contacts from macOS Contacts.app. Use when resolving phone numbers to names, finding contact info, or searching the address book.
metadata: {"clawdbot":{"emoji":"👤","os":["darwin"]}}
---

# macos-contacts

Use osascript to query macOS Contacts.app.

## Requirements
- Contacts.app with data
- Automation permission for terminal

## Quick Lookups (one-liners)

**Lookup by phone (name only):**
```bash
osascript -e 'tell application "Contacts" to get name of every person whose value of phones contains "+15551234567"'
```

**Lookup by name (names only):**
```bash
osascript -e 'tell application "Contacts" to get name of every person whose name contains "Tyler"'
```

**List all contacts:**
```bash
osascript -e 'tell application "Contacts" to get name of every person'
```

## Full Contact Info

⚠️ **Don't use `first person whose`** - it crashes with error -1719 when no match is found. Use `every person whose` and check the list length instead.

**By phone:**
```bash
osascript -e 'tell application "Contacts"
  set matches to every person whose value of phones contains "+15551234567"
  if length of matches > 0 then
    set p to item 1 of matches
    return {name of p, value of phones of p, value of emails of p}
  else
    return {}
  end if
end tell'
```

**By name:**
```bash
osascript -e 'tell application "Contacts"
  set matches to every person whose name contains "John Smith"
  if length of matches > 0 then
    set p to item 1 of matches
    return {name of p, value of phones of p, value of emails of p}
  else
    return {}
  end if
end tell'
```

**Get ALL matches (loop):**
```bash
osascript -e 'tell application "Contacts"
  set matches to every person whose name contains "Tyler"
  set results to {}
  repeat with p in matches
    set end of results to {name of p, value of phones of p}
  end repeat
  return results
end tell'
```

## Phone Format Quirks

⚠️ **Phone lookup is EXACT STRING MATCHING** - the search string must appear exactly as stored.

| Stored Format | Search String | Works? |
|---------------|---------------|--------|
| `+15551234567` | `+15551234567` | ✅ |
| `+15551234567` | `5551234567` | ❌ |
| `+15551234567` | `(555) 123-4567` | ❌ |
| `(555) 123-4567` | `(555) 123-4567` | ✅ |

**Tip:** Contacts stores numbers in various formats. If lookup fails:
1. First try with `+1` prefix: `+1XXXXXXXXXX`
2. If that fails, search by the last 7 digits as a partial match won't help
3. Consider searching by name instead if you know it

## Name Search Behavior

- **Case-insensitive:** `tyler`, `Tyler`, and `TYLER` all work
- **Partial match:** `contains "Ty"` matches "Tyler"
- **Exact match:** Use `is` instead of `contains` for exact: `whose name is "Tyler Yust"`
- **Multiple results:** Returns comma-separated list

## Edge Cases

| Input | Result |
|-------|--------|
| Empty string `""` | No output (not an error) |
| Non-existent name | No output |
| Non-existent phone | No output |
| Special chars (apostrophe) | Works with proper escaping: `'O'\''Brien'` |
| Duplicate contacts | Returns all matches |

## Error Handling

- **No matches:** Returns empty output (exit code 0), not an error
- **Permission denied:** First run may prompt for Contacts access
- **-1719 error:** Happens when using `first person whose` with no match (AppleScript crashes). Always use `every person whose` and check list length first
- **Missing fields:** If a contact has no phone or email, those fields return empty (no error)

## Output Format

The full lookup returns comma-separated values in this order:
```
<name>, <phone1>, [phone2...], <email1>, [email2...]
```

| Contact State | Output Example |
|---------------|----------------|
| Has phone + email | `John Smith, +15551234567, john@example.com` |
| Has phone, no email | `Jane Doe, +15559876543,` (trailing comma) |
| Multiple phones | `Name, +1111, +2222, email@x.com` |
| No name (empty) | `, +15550000000,` (leading comma) |
| No match | (empty output) |

## List All Contacts

```bash
# Get all names (comma-separated)
osascript -e 'tell application "Contacts" to get name of every person'

# Get count
osascript -e 'tell application "Contacts" to count every person'
```

**Note:** Empty names appear as `""` or blank in the list.

## Birthday & Address Fields

**Get birthday:**
```bash
osascript -e 'tell application "Contacts"
  set matches to every person whose name contains "John Smith"
  if length of matches > 0 then
    set p to item 1 of matches
    return birth date of p
  else
    return "not found"
  end if
end tell'
```
Returns format: `date "Saturday, January 15, 1990 at 12:00:00 AM"` or `missing value` if not set.

**Get address:**
```bash
osascript -e 'tell application "Contacts"
  set matches to every person whose name contains "John Smith"
  if length of matches > 0 then
    set p to item 1 of matches
    return {street of addresses of p, city of addresses of p, state of addresses of p, zip of addresses of p}
  else
    return "not found"
  end if
end tell'
```
Returns nested lists: `{{street1}, {city1}, {state1}, {zip1}}` - one set per address.

**Address fields available:** `street`, `city`, `state`, `zip`, `country`, `country code`

## Create Contact

**Create with name only:**
```bash
osascript -e 'tell application "Contacts"
  set newPerson to make new person with properties {first name:"John", last name:"Doe"}
  save
end tell'
```

**Create with phone:**
```bash
osascript -e 'tell application "Contacts"
  set newPerson to make new person with properties {first name:"Test", last name:"McTestface"}
  make new phone at end of phones of newPerson with properties {label:"mobile", value:"+15555555555"}
  save
end tell'
```

**Create with phone and email:**
```bash
osascript -e 'tell application "Contacts"
  set newPerson to make new person with properties {first name:"Test", last name:"McTestface"}
  make new phone at end of phones of newPerson with properties {label:"mobile", value:"+15555555555"}
  make new email at end of emails of newPerson with properties {label:"home", value:"test@example.com"}
  save
end tell'
```

**Available labels:**
- Phone: `mobile`, `home`, `work`, `main`, `iPhone`, `other`
- Email: `home`, `work`, `other`

⚠️ **Always call `save`** at the end or changes won't persist.

## Edit Contact

**Add phone to existing contact:**
```bash
osascript -e 'tell application "Contacts"
  set matches to every person whose name contains "Test McTestface"
  if length of matches > 0 then
    set p to item 1 of matches
    make new phone at end of phones of p with properties {label:"work", value:"+16666666666"}
    save
    return "phone added"
  else
    return "contact not found"
  end if
end tell'
```

**Add email to existing contact:**
```bash
osascript -e 'tell application "Contacts"
  set matches to every person whose name contains "Test McTestface"
  if length of matches > 0 then
    set p to item 1 of matches
    make new email at end of emails of p with properties {label:"work", value:"test@test.com"}
    save
    return "email added"
  else
    return "contact not found"
  end if
end tell'
```

**Update name:**
```bash
osascript -e 'tell application "Contacts"
  set matches to every person whose name contains "Test McTestface"
  if length of matches > 0 then
    set p to item 1 of matches
    set first name of p to "Updated"
    set last name of p to "Name"
    save
    return "name updated"
  else
    return "contact not found"
  end if
end tell'
```

**Set birthday:**
```bash
osascript -e 'tell application "Contacts"
  set matches to every person whose name contains "Test McTestface"
  if length of matches > 0 then
    set p to item 1 of matches
    set birth date of p to date "January 1, 1990"
    save
    return "birthday set"
  else
    return "contact not found"
  end if
end tell'
```

## Delete Contact

**Delete by name:**
```bash
osascript -e 'tell application "Contacts"
  set matches to every person whose name contains "Test McTestface"
  if length of matches > 0 then
    delete item 1 of matches
    save
    return "deleted"
  else
    return "contact not found"
  end if
end tell'
```

**Delete ALL matching contacts (careful!):**
```bash
osascript -e 'tell application "Contacts"
  set matches to every person whose name contains "Test McTestface"
  repeat with p in matches
    delete p
  end repeat
  save
  return "deleted all matches"
end tell'
```

⚠️ **Delete is permanent** - there's no undo. Always verify the match first with a lookup before deleting.

## Notes

- Phone format must match storage. Try with/without +1 if lookup fails.
- Use `contains` for fuzzy match, `is` for exact.
- Duplicate contacts are common - some people may have multiple entries in the address book.
- Empty name contacts exist - they still have phone/email data, just no name field.
