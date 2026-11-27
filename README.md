# Yoohoo for Home Assistant

Send your Home Assistant alerts to [Yoohoo](https://yoohoo.buzz). Each automation picks a level. The alerts that matter reach your phone right away, and the rest wait for one roundup at 6 pm.

A door left open buzzes you now. The washer finishing, a low battery or the bins going out tomorrow can wait until evening.

## Install

You need the Yoohoo app ([iPhone, Android or web](https://yoohoo.buzz/download?ref=hacs)), [HACS](https://hacs.xyz) and Home Assistant 2026.3 or newer.

1. In the Yoohoo app, open **Add a source**, pick **Home Assistant** and copy the link.
2. In Home Assistant, open HACS, search for **Yoohoo** and download it. Restart Home Assistant.
3. Go to **Settings**, then **Devices & services**, then **Add integration**, and pick **Yoohoo**.
4. Paste the link. A "Home Assistant connected" alert shows up in Yoohoo.

## Send an alert

Use the action **Yoohoo: Send alert** in an automation or script.

```yaml
action: yoohoo.send_alert
data:
  title: Washer is done
  level: roundup
  group: washer
```

| Level | What happens |
| --- | --- |
| `roundup` (For the roundup) | Waits for the 6 pm roundup. The default. |
| `needs_me` (Needs me) | Reaches you right away. |
| `wrong` (Something is wrong) | Reaches you right away. |
| `all_good` (All good) | Stays quiet, and settles earlier problems in the same `group`. |

Other fields: `message` for detail under the title, `group` to keep related alerts together, `url` for a page to open from the alert, and `config_entry_id` if you've set up more than one Yoohoo source.

The integration also adds a **Yoohoo** notify entity, so `notify.send_message` works too. Those alerts wait for the roundup.

If Home Assistant can't reach Yoohoo, the integration skips that alert and writes a warning to the log, so your automation keeps running. If the link stops working, Repairs tells you.

## Privacy

The integration sends only what you put in the action (title, message, group, link) to your own private Yoohoo link. See [Yoohoo's privacy policy](https://yoohoo.buzz/privacy).

## Help

Full guide: [yoohoo.buzz/docs/sources/home-assistant](https://yoohoo.buzz/docs/sources/home-assistant). Problems with the integration: [open an issue](https://github.com/RakeshPotnuru/ha-yoohoo/issues).
